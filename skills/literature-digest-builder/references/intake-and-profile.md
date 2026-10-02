# Intake and profile design

Collect only information that changes the result.

## Required decisions

- Profile name and stable lowercase ID.
- Research direction and the concepts that must be included.
- Specialist core journals and broad journals, if the user has preferences.
- Whether reviews, systematic reviews, meta-analyses, editorials, letters, and preprints are wanted.
- Daily ordinary quota and any additive priority topic that should bypass that quota.
- Delivery timezone, primary time, fallback time, recipient-secret name, and output language.
- GitHub repository to deploy into, or whether a new fork is desired.

## Safe defaults

- Sources: PubMed, arXiv, bioRxiv, and medRxiv for biomedical topics; disable irrelevant preprint sources for other fields.
- PubMed windows: publication date 7 days and entry date 14 days.
- PubMed result cap: 500 per query window.
- Ordinary quota: 30 papers.
- Public journal-quality proxy: SJR >= 1.5, with the metric name, year, and source shown explicitly.
- Ordering: peer-reviewed/PubMed before preprints, then relevance with a small journal-quality bonus.
- State: 30-day sent history, 2,000-item pending queue, no-new-items email enabled.
- Reliability: primary GitHub schedule, fallback GitHub schedule, and an independent later watchdog.

Do not require Zotero if a configured topic profile can be used for reranking. If Zotero is used, ask whether the whole library or only named collections should form the relevance corpus.

## Translate natural language into policy

Preserve distinctions such as:

- “all papers from these journals” -> core journal retrieval;
- “only papers about this topic from Nature/Science/Cell” -> topic-constrained broad journals;
- “send every paper about X” -> additive priority topic;
- “reviews are acceptable” -> explicitly allowed publication types, not removal of all type filtering;
- “impact factor above 5” without licensed JCR data -> explain the limitation and offer a named public SJR/CiteScore threshold instead.

