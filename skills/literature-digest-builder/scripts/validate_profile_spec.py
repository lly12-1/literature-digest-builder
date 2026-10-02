#!/usr/bin/env python3
"""Validate a literature-digest profile specification using only stdlib."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


PROFILE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SECRET_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")
REPOSITORY = re.compile(r"^[^/\s]+/[^/\s]+$")


def load_spec(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("profile specification must be a JSON object")
    return value


def validate(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_strings = (
        "profile_id",
        "display_name",
        "repository",
        "receiver_secret",
        "pubmed_query",
    )
    for key in required_strings:
        if not isinstance(spec.get(key), str) or not spec[key].strip():
            errors.append(f"{key} must be a non-empty string")

    profile_id = spec.get("profile_id", "")
    if isinstance(profile_id, str) and profile_id and not PROFILE_ID.fullmatch(profile_id):
        errors.append("profile_id must use lowercase letters, digits, and single hyphens")
    receiver_secret = spec.get("receiver_secret", "")
    if isinstance(receiver_secret, str) and receiver_secret and not SECRET_NAME.fullmatch(receiver_secret):
        errors.append("receiver_secret must be an uppercase GitHub Secret name")
    repository = spec.get("repository", "")
    if isinstance(repository, str) and repository and not REPOSITORY.fullmatch(repository):
        errors.append("repository must have owner/repository form")

    for key, minimum in (
        ("max_papers", 1),
        ("lookback_days", 1),
        ("entry_lookback_days", 1),
        ("retmax", 1),
        ("sent_history_days", 1),
        ("pending_max_papers", 1),
        ("journal_zero_alert_days", 1),
    ):
        value = spec.get(key)
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < minimum):
            errors.append(f"{key} must be an integer >= {minimum}")
    min_sjr = spec.get("min_sjr")
    if min_sjr is not None and (
        not isinstance(min_sjr, (int, float))
        or isinstance(min_sjr, bool)
        or min_sjr < 0
    ):
        errors.append("min_sjr must be a non-negative number")

    journals = spec.get("journals")
    if not isinstance(journals, list) or not journals:
        errors.append("journals must be a non-empty array")
    else:
        seen: set[str] = set()
        for index, journal in enumerate(journals):
            prefix = f"journals[{index}]"
            if not isinstance(journal, dict):
                errors.append(f"{prefix} must be an object")
                continue
            name = journal.get("name")
            if not isinstance(name, str) or not name.strip():
                errors.append(f"{prefix}.name must be a non-empty string")
            elif name.casefold() in seen:
                errors.append(f"duplicate journal name: {name}")
            else:
                seen.add(name.casefold())
            if not isinstance(journal.get("aliases", []), list):
                errors.append(f"{prefix}.aliases must be an array")
            sjr = journal.get("sjr")
            if not isinstance(sjr, (int, float)) or isinstance(sjr, bool) or sjr < 0:
                errors.append(f"{prefix}.sjr must be a non-negative number")
            if not isinstance(journal.get("year"), int):
                errors.append(f"{prefix}.year must be an integer")
            if not isinstance(journal.get("core"), bool):
                errors.append(f"{prefix}.core must be boolean")
            source_url = journal.get("source_url")
            if not isinstance(source_url, str) or not source_url.startswith(("https://", "http://")):
                errors.append(f"{prefix}.source_url must be an HTTP(S) URL")

    priority_topics = spec.get("priority_topics", [])
    if not isinstance(priority_topics, list):
        errors.append("priority_topics must be an array")
    else:
        for index, topic in enumerate(priority_topics):
            if not isinstance(topic, dict):
                errors.append(f"priority_topics[{index}] must be an object")
                continue
            for key in ("name", "query"):
                if not isinstance(topic.get(key), str) or not topic[key].strip():
                    errors.append(f"priority_topics[{index}].{key} must be non-empty")
            if not isinstance(topic.get("keywords", []), list):
                errors.append(f"priority_topics[{index}].keywords must be an array")

    schedule = spec.get("schedule", {})
    if not isinstance(schedule, dict):
        errors.append("schedule must be an object")
    else:
        for key in ("timezone", "primary_cron_utc", "fallback_cron_utc"):
            value = schedule.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"schedule.{key} must be a non-empty string")

    sources = spec.get("sources", {})
    if sources and not isinstance(sources, dict):
        errors.append("sources must be an object")
    topic_keywords = spec.get("topic_keywords", [])
    preprints_enabled = isinstance(sources, dict) and any(
        sources.get(key, False)
        for key in ("arxiv_enabled", "biorxiv_enabled", "medrxiv_enabled")
    )
    if preprints_enabled and (not isinstance(topic_keywords, list) or not topic_keywords):
        errors.append("topic_keywords must be non-empty when preprint sources are enabled")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    args = parser.parse_args()
    try:
        spec = load_spec(args.spec)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    errors = validate(spec)
    if errors:
        for error in errors:
            print(f"INVALID: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {spec['profile_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

