# Generated personal skill contract

The renderer creates `skills/<profile-id>-literature-digest/`.

The personal skill must:

- identify the exact repository, workflow file, profile config, and state/cache prefix;
- describe the research scope, core-journal rule, ordinary quota, and priority-topic behavior;
- support status checks, safe manual retry, configuration updates, and diagnosis;
- treat a run as successful only when email delivery and state persistence are visible in logs;
- avoid duplicate delivery when the local date is already complete;
- never reveal or request secret values in ordinary status output;
- distinguish a source outage, zero new literature, filtering to zero, SMTP failure, LLM failure, cache failure, and scheduler delay.

The generated skill is an operational interface for one deployment. It should not contain a copy of the generic builder or credentials.

