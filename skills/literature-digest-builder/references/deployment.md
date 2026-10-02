# Deployment

## Preparation

Use a clean checkout of a compatible runtime. Do not overwrite unrelated local changes. Generate into a branch or isolated worktree when the repository is already in use.

Required GitHub Secrets normally include:

- `ZOTERO_ID` and `ZOTERO_KEY` when Zotero reranking is enabled;
- `SENDER` and `SENDER_PASSWORD`;
- the profile's `receiver_secret`;
- `OPENAI_API_KEY` or the compatible LLM provider key;
- `NCBI_API_KEY`.

Use repository Variables for non-sensitive values such as SMTP host/port, API base URL, model name, and debug flags. Never print secret values while checking configuration.

## Review before push

Check:

- UTC cron conversion and daylight-saving implications;
- unique workflow file, concurrency group, cache key, and state path;
- journal names and aliases against PubMed;
- whether core journals really should bypass topic filtering;
- whether an additive priority topic can make the email exceed the ordinary quota;
- no personal address or credential appears in committed files.

## Test

Run local validation, then trigger one manual GitHub workflow. Verify logs for:

- a nonzero successful-source count;
- per-source retrieval counts;
- topic and sent-history filtering counts;
- selected peer-reviewed/preprint counts;
- `Email sent successfully`;
- persisted sent history;
- the correct local-date completion marker.

Trigger once more only when testing idempotency: it should skip because the date is already complete. Use force/resend modes only when their duplicate-email implications are understood.

## Scheduling caveat

GitHub cron can be delayed. A second cron in the same service improves retry opportunity but is not independent infrastructure. An optional local Codex watchdog can inspect the day's workflow and dispatch a retry; it depends on the local host, authentication, and its own availability.

