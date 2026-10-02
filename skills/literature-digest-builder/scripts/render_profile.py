#!/usr/bin/env python3
"""Render a runtime profile, workflow, journal table, and personal skill."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from validate_profile_spec import load_spec, validate


def scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def yaml_list(values: list[Any], indent: int) -> str:
    pad = " " * indent
    if not values:
        return f"{pad}[]"
    return "\n".join(f"{pad}- {scalar(value)}" for value in values)


def defaults(spec: dict[str, Any]) -> dict[str, Any]:
    merged = {
        "language": "Chinese",
        "max_papers": 30,
        "min_sjr": 1.5,
        "lookback_days": 7,
        "entry_lookback_days": 14,
        "retmax": 500,
        "sent_history_days": 30,
        "pending_max_papers": 2000,
        "journal_zero_alert_days": 3,
        "send_empty": True,
        "core_journals_bypass_topic": True,
        "topic_keywords": [],
        "ranking_profile": [],
        "priority_topics": [],
        "publication_types": {
            "exclude": ["Editorial", "Comment", "Letter", "News"],
            "core_allow": ["Review", "Systematic Review", "Meta-Analysis"],
            "priority_allow": ["Review", "Systematic Review", "Meta-Analysis"],
        },
        "sources": {
            "arxiv_enabled": True,
            "arxiv_categories": [],
            "biorxiv_enabled": True,
            "biorxiv_categories": [],
            "medrxiv_enabled": True,
            "medrxiv_categories": [],
        },
    }
    merged.update(spec)
    return merged


def render_config(spec: dict[str, Any]) -> str:
    profile_id = spec["profile_id"]
    display_name = spec["display_name"]
    core = [row["name"] for row in spec["journals"] if row["core"]]
    sources = spec["sources"]
    enabled_sources = ["pubmed"]
    for name in ("arxiv", "biorxiv", "medrxiv"):
        if sources.get(f"{name}_enabled", False):
            enabled_sources.append(name)
    publication = spec["publication_types"]
    priority = spec["priority_topics"]
    priority_query = " OR ".join(f"({item['query']})" for item in priority) or None
    priority_keywords = [
        keyword
        for item in priority
        if item.get("additive", False)
        for keyword in item.get("keywords", [])
    ]
    lines = [
        "defaults:",
        "  - base",
        "  - _self_",
        "",
        "email:",
        "  sender: ${oc.env:SENDER}",
        "  receiver: ${oc.env:RECEIVER}",
        "  smtp_server: ${oc.env:SMTP_SERVER,smtp.qq.com}",
        "  smtp_port: ${oc.env:SMTP_PORT,465}",
        "  sender_password: ${oc.env:SENDER_PASSWORD}",
        f"  subject: {scalar(display_name)}",
        f"  digest_name: {scalar(display_name)}",
        f"  empty_subject: {scalar(display_name + ': no new literature today')}",
        f"  alert_subject: {scalar('⚠️ ' + display_name + ': retrieval alert')}",
        "",
        "llm:",
        "  api:",
        "    key: ${oc.env:OPENAI_API_KEY}",
        "    base_url: ${oc.env:OPENAI_API_BASE,https://api.deepseek.com}",
        "  generation_kwargs:",
        "    model: ${oc.env:LLM_MODEL,deepseek-chat}",
        "    max_tokens: 16384",
        f"  language: {scalar(spec['language'])}",
        "",
        "reranker:",
        "  local:",
        "    model: sentence-transformers/all-MiniLM-L6-v2",
        "    encode_kwargs: null",
        "",
        "source:",
        "  arxiv:",
        f"    category: {json.dumps(sources.get('arxiv_categories', []), ensure_ascii=False)}",
        "    include_cross_list: true",
        "  biorxiv:",
        "    category:",
        yaml_list(sources.get("biorxiv_categories", []), 6),
        "  medrxiv:",
        "    category:",
        yaml_list(sources.get("medrxiv_categories", []), 6),
        "  pubmed:",
        f"    journal_metrics_file: config/{profile_id}_journals.csv",
        f"    min_sjr: {spec['min_sjr']}",
        f"    lookback_days: {spec['lookback_days']}",
        f"    entry_lookback_days: {spec['entry_lookback_days']}",
        f"    retmax: {spec['retmax']}",
        "    restrict_search_to_journal_metrics: true",
        f"    core_journals_bypass_topic: {scalar(spec['core_journals_bypass_topic'])}",
        "    core_journals:",
        yaml_list(core, 6),
        "    api_key: ${oc.env:NCBI_API_KEY,null}",
        "    exclude_publication_types:",
        yaml_list(publication.get("exclude", []), 6),
        "    core_allowed_publication_types:",
        yaml_list(publication.get("core_allow", []), 6),
        "    priority_allowed_publication_types:",
        yaml_list(publication.get("priority_allow", []), 6),
        f"    query: {scalar(spec['pubmed_query'])}",
        f"    priority_query: {scalar(priority_query)}",
        "",
        "executor:",
        f"  send_empty: {scalar(spec['send_empty'])}",
        f"  max_paper_num: {spec['max_papers']}",
        f"  source: {json.dumps(enabled_sources)}",
        "  reranker: local",
        f"  sent_history_path: ${{oc.env:SENT_HISTORY_PATH,.state/{profile_id}-sent-history.json}}",
        f"  sent_history_days: {spec['sent_history_days']}",
        f"  pending_max_papers: {spec['pending_max_papers']}",
        f"  journal_zero_alert_days: {spec['journal_zero_alert_days']}",
        f"  daily_timezone: {scalar(spec['schedule']['timezone'])}",
        "  force_run: ${oc.decode:${oc.env:FORCE_RUN,false}}",
        "  mark_today_complete_only: false",
        "  topic_keywords:",
        yaml_list(spec["topic_keywords"], 4),
        "  ranking_profile:",
        yaml_list(spec["ranking_profile"], 4),
        "  priority_topic_keywords:",
        yaml_list(priority_keywords, 4),
        "  pubmed_sjr_bonus: 0.12",
        "",
    ]
    return "\n".join(lines)


def render_workflow(spec: dict[str, Any]) -> str:
    profile_id = spec["profile_id"]
    receiver_secret = spec["receiver_secret"]
    schedule = spec["schedule"]
    return f'''name: {spec["display_name"]}
on:
  workflow_dispatch:
    inputs:
      force_run:
        description: Ignore today's completion marker and run normally
        required: false
        default: false
        type: boolean
  schedule:
    # {schedule.get("local_time_note", "Configured local schedule")} ({schedule["timezone"]})
    - cron: '{schedule["primary_cron_utc"]}'
    - cron: '{schedule["fallback_cron_utc"]}'

concurrency:
  group: {profile_id}
  cancel-in-progress: false

jobs:
  calculate-and-send:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6
      - name: Setup uv
        uses: astral-sh/setup-uv@v7
      - name: Restore history
        uses: actions/cache/restore@v5
        with:
          path: .state/{profile_id}-sent-history.json
          key: {profile_id}-history-${{{{ github.run_id }}}}
          restore-keys: |
            {profile_id}-history-
      - name: Run digest
        env:
          ZOTERO_ID: ${{{{ secrets.ZOTERO_ID }}}}
          ZOTERO_KEY: ${{{{ secrets.ZOTERO_KEY }}}}
          SENDER: ${{{{ secrets.SENDER }}}}
          RECEIVER: ${{{{ secrets.{receiver_secret} }}}}
          SENDER_PASSWORD: ${{{{ secrets.SENDER_PASSWORD }}}}
          SMTP_SERVER: ${{{{ vars.SMTP_SERVER || 'smtp.qq.com' }}}}
          SMTP_PORT: ${{{{ vars.SMTP_PORT || '465' }}}}
          OPENAI_API_KEY: ${{{{ secrets.OPENAI_API_KEY }}}}
          OPENAI_API_BASE: ${{{{ vars.OPENAI_API_BASE || 'https://api.deepseek.com' }}}}
          LLM_MODEL: ${{{{ vars.LLM_MODEL || 'deepseek-chat' }}}}
          NCBI_API_KEY: ${{{{ secrets.NCBI_API_KEY }}}}
          SENT_HISTORY_PATH: .state/{profile_id}-sent-history.json
          FORCE_RUN: ${{{{ inputs.force_run || 'false' }}}}
        run: uv run src/zotero_arxiv_daily/main.py --config-name {profile_id}
      - name: Save history
        if: ${{{{ success() && hashFiles('.state/{profile_id}-sent-history.json') != '' }}}}
        uses: actions/cache/save@v5
        with:
          path: .state/{profile_id}-sent-history.json
          key: {profile_id}-history-${{{{ github.run_id }}}}
'''


def render_personal_skill(spec: dict[str, Any]) -> str:
    profile_id = spec["profile_id"]
    priority = [item["name"] for item in spec["priority_topics"]]
    priority_text = ", ".join(priority) if priority else "none"
    return f'''---
name: {profile_id}-literature-digest
description: Operate, update, and diagnose the {spec["display_name"]} deployment in {spec["repository"]}. Use for status checks, safe retries, profile changes, and missed or duplicate digest investigations.
---

# {spec["display_name"]}

Repository: `{spec["repository"]}`  
Workflow: `.github/workflows/{profile_id}.yml`  
Profile: `config/{profile_id}.yaml`  
State: `.state/{profile_id}-sent-history.json`

The ordinary daily quota is {spec["max_papers"]}. Additive priority topics: {priority_text}. Peer-reviewed PubMed records are ordered before preprints. Never expose GitHub Secrets or credential values.

## Status and retry

Inspect all runs for the current date in `{spec["schedule"]["timezone"]}`. A green badge alone is insufficient: confirm `Email sent successfully`, persisted history, and the correct completion marker. If the day is already complete, do not trigger a duplicate.

If no successful run exists, inspect source, LLM, SMTP, and cache errors. Retry the existing workflow once with `force_run=true` only when the completion marker is absent. After dispatch, wait for completion and report retrieval counts, selected peer-reviewed/preprint counts, source failures, and the run URL.

## Changes

For topic, journal, quota, type, schedule, or recipient-secret changes, edit only this profile's config, journal CSV, workflow, and tests. Preserve sent history, pending queue, source-failure semantics, and unique state/cache/concurrency names. Validate before pushing and perform a test email only with user authorization.
'''


def write_text(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite {path}; pass --force")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_journals(path: Path, spec: dict[str, Any], force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite {path}; pass --force")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("journal", "aliases", "sjr", "quartile", "year", "source_url"),
        )
        writer.writeheader()
        for journal in spec["journals"]:
            writer.writerow(
                {
                    "journal": journal["name"],
                    "aliases": "|".join(journal.get("aliases", [])),
                    "sjr": journal["sjr"],
                    "quartile": journal.get("quartile", ""),
                    "year": journal["year"],
                    "source_url": journal["source_url"],
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        spec = load_spec(args.spec)
        errors = validate(spec)
        if errors:
            raise ValueError("; ".join(errors))
        spec = defaults(spec)
        profile_id = spec["profile_id"]
        write_text(args.output / "config" / f"{profile_id}.yaml", render_config(spec), args.force)
        write_journals(args.output / "config" / f"{profile_id}_journals.csv", spec, args.force)
        write_text(args.output / ".github" / "workflows" / f"{profile_id}.yml", render_workflow(spec), args.force)
        skill_root = args.output / "skills" / f"{profile_id}-literature-digest"
        write_text(skill_root / "SKILL.md", render_personal_skill(spec), args.force)
        write_text(
            skill_root / "references" / "profile.json",
            json.dumps(spec, ensure_ascii=False, indent=2) + "\n",
            args.force,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Rendered profile and personal skill: {profile_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

