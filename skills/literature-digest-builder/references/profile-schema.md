# Profile specification schema

The renderer accepts UTF-8 JSON. Start from `assets/example-profile.json` and preserve these fields.

## Required top-level fields

- `profile_id`: lowercase letters, digits, and hyphens; used in file names, state, cache, workflow, and child-skill identity.
- `display_name`: user-facing digest name.
- `repository`: `owner/repository` used by the generated child skill.
- `receiver_secret`: GitHub Secret name containing the recipient address.
- `pubmed_query`: complete topic-only PubMed expression; journal clauses are added by the runtime.
- `journals`: non-empty array of journal records.

## Optional fields and defaults

- `language`: `Chinese`.
- `max_papers`: `30`.
- `min_sjr`: `1.5`.
- `lookback_days`: `7`.
- `entry_lookback_days`: `14`.
- `retmax`: `500`.
- `sent_history_days`: `30`.
- `pending_max_papers`: `2000`.
- `journal_zero_alert_days`: `3`.
- `send_empty`: `true`.
- `core_journals_bypass_topic`: `true`.
- `topic_keywords`: array used for cross-source filtering.
- `ranking_profile`: natural-language relevance descriptions. When non-empty, the runtime need not learn from a Zotero corpus.
- `priority_topics`: objects with `name`, `query`, `keywords`, `additive`, `bypass_journal_filter`, and `include_reviews`.
- `publication_types`: `exclude`, `core_allow`, and `priority_allow` arrays.
- `sources`: arXiv, bioRxiv, and medRxiv category arrays plus booleans.
- `schedule`: `timezone`, `primary_cron_utc`, `fallback_cron_utc`, and a human-readable local-time note.

## Journal record

Each `journals` element contains:

- `name`;
- `aliases`, an array;
- `sjr`, a non-negative number;
- `quartile`;
- `year`;
- `source_url`;
- `core`, a boolean.

Only rows meeting `min_sjr` are ordinary whitelist journals. A core or priority bypass must be intentional and visible.

