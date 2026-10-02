# Literature Digest Builder

A reusable Codex skill that turns a research direction into a personal daily scholarly-literature email system.

Users describe their field, topics, target journals, article types, schedule, and delivery preferences in natural language. The skill creates:

- a PubMed/MeSH search policy;
- specialist and multidisciplinary journal rules;
- a journal alias and public-metric table;
- a deployable digest profile;
- a GitHub Actions workflow;
- persistent sent-history and overflow-queue settings;
- a personal follow-up skill for status checks, safe retries, updates, and diagnosis.

It is based on lessons from a production neurodegeneration digest, but contains no personal email address, password, API key, Zotero credential, or private repository data.

## Install

Ask Codex:

> Install the skill from https://github.com/lly12-1/literature-digest-builder/tree/main/skills/literature-digest-builder

Or use the standard Codex skill installer:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo lly12-1/literature-digest-builder \
  --path skills/literature-digest-builder
```

The skill becomes available on the next Codex turn as `$literature-digest-builder`.

## Example

```text
Use $literature-digest-builder to build a daily nephrology literature digest.
Focus on IgA nephropathy, diabetic kidney disease, and renal fibrosis.
Retrieve specialist core journals broadly, constrain multidisciplinary journals
to the topics, include systematic reviews, and send at 07:00 Asia/Shanghai.
```

The agent first designs an auditable profile. It asks only for decisions that materially change retrieval or authorize external actions. Forking a repository, pushing files, setting GitHub Secrets, creating schedules, and sending a test email remain explicit deployment actions.

## Reliability model

Generated profiles preserve the following defaults unless the user chooses otherwise:

- PubMed publication-date and entry-date windows are unioned and deduplicated;
- long NCBI requests use POST;
- journal constraints are applied during search;
- peer-reviewed records rank before preprints;
- sent history and an overflow queue persist across runs;
- a failed source prevents the complete-day marker;
- duplicate schedules are made idempotent by the daily marker;
- success requires email-delivery and state-persistence evidence in logs;
- SJR or CiteScore is never mislabeled as Journal Impact Factor.

## Runtime

The generated profile targets a compatible `zotero-arxiv-daily` runtime. The currently validated reference implementation is [lly12-1/zotero-arxiv-daily](https://github.com/lly12-1/zotero-arxiv-daily). The builder does not modify or deploy to any repository without user authorization.

## Security

Generated files contain only GitHub Secret names, never secret values. Email authorization codes, LLM keys, NCBI keys, and Zotero keys belong in GitHub Actions Secrets. Non-sensitive SMTP, model, and API-base settings belong in repository Variables.

## License

MIT

