---
name: literature-digest-builder
description: Create, customize, deploy, and maintain a reusable daily scholarly-literature email digest from a user's research direction, target journals, sources, schedule, and delivery preferences. Use when a user wants recurring paper alerts or a personal literature-push skill, not for a one-off literature search.
---

# Literature Digest Builder

Turn a user's research direction into two auditable outputs:

1. a deployable profile for the compatible `zotero-arxiv-daily` runtime; and
2. a personal `<profile-id>-literature-digest` skill that can operate and diagnose that deployment later.

Do not embed personal credentials, email passwords, API keys, Zotero keys, or secret values in generated files. External actions such as forking, pushing, setting GitHub Secrets, sending a test email, or creating a scheduled automation require the user's authorization at the point of action.

## Modes

- **Design:** turn a research direction into a search and filtering policy.
- **Build:** generate the profile, journal table, workflow, tests/checks, and personal child skill.
- **Deploy:** fork or update a compatible runtime repository, configure GitHub, and perform one test run.
- **Maintain:** change topics, journals, quotas, recipients, or schedules without affecting other profiles.
- **Diagnose:** inspect runs and logs, then repair the smallest failing layer without weakening deduplication.

## Workflow

1. Capture the minimum consequential inputs. Read [references/intake-and-profile.md](references/intake-and-profile.md). Infer safe defaults when the user has not expressed a preference; ask only when a missing value would materially change retrieval or cause an external side effect.
2. Design the retrieval policy. For medical or life-science profiles, use MeSH plus title/abstract synonyms and distinguish clinical, translational, basic, and evidence-synthesis material. Read [references/retrieval-policy.md](references/retrieval-policy.md).
3. Separate specialist core journals from broad multidisciplinary journals. Core journals may be retrieved in full; broad journals must remain topic-constrained unless the user explicitly chooses otherwise. Record aliases and a public metric with its year and source. Never label SJR or CiteScore as JIF.
4. Write a JSON profile specification matching [references/profile-schema.md](references/profile-schema.md). Validate it with `scripts/validate_profile_spec.py`.
5. Run `scripts/render_profile.py` into a clean compatible runtime checkout. The renderer creates a domain config, journal CSV, GitHub workflow, and personal child skill. Review the generated query, journal policy, schedule, and secret names before deployment.
6. Validate syntax and invariants locally. Confirm that profile IDs, workflow names, state paths, cache keys, receiver secrets, and concurrency groups are unique. Add domain-specific regression cases for journal aliases, topic rules, priority topics, and excluded publication types.
7. For deployment, read [references/deployment.md](references/deployment.md). Keep credentials in GitHub Secrets and non-sensitive settings in repository Variables. Trigger exactly one test run and verify retrieval counts, email success, persisted history, and the daily completion marker.
8. Deliver the generated personal skill and a concise runbook. The child skill must know the repository, workflow, profile, safe retry policy, and success evidence. Read [references/generated-skill-contract.md](references/generated-skill-contract.md).

## Reliability Invariants

Preserve these unless the user explicitly requests a different policy and understands the tradeoff:

- query publication-date and database-entry-date windows, then union and deduplicate;
- apply journal constraints during PubMed search so broad results do not consume the result cap;
- use POST for long NCBI requests;
- prioritize peer-reviewed/PubMed records before preprints;
- persist sent history and an overflow queue;
- send a short no-new-items notice when configured;
- do not mark a day complete when any configured source failed;
- make duplicate scheduled triggers safe through a daily completion marker;
- verify an actual email-success log and state persistence, not merely a green workflow badge;
- never silently convert a public metric threshold into an impact-factor claim.

## Compatible Runtime

The validated reference implementation is `https://github.com/lly12-1/zotero-arxiv-daily`. Treat it as a configurable default, not as permission to modify that repository. A different repository may be used if it supports the generated config and workflow contract.

