# Retrieval policy

## Search construction

For biomedical topics, build each concept from:

- controlled vocabulary such as MeSH;
- full names and abbreviations;
- spelling, punctuation, and historical-name variants;
- gene/protein symbols only when disambiguated by context;
- title/abstract phrases for emerging concepts without mature indexing.

Combine synonyms with `OR` and distinct required concepts with `AND`. Keep the main topic query separate from journal clauses so the runtime can apply different rules to specialist and multidisciplinary journals.

## Journal tiers

- **Core specialist journals:** retrieve all recent records, optionally bypassing the topic filter. This is appropriate only when the whole journal is relevant to the user's field.
- **Broad or multidisciplinary journals:** require the topic query and journal match together.
- **Priority topic:** retrieve independently of the ordinary journal threshold only when the user explicitly wants comprehensive coverage.

Every journal row should contain a canonical name, PubMed aliases, metric, quartile, metric year, and source URL. Add regression cases for names containing ampersands, commas, apostrophes, abbreviations, or historical titles.

## Evidence and article types

Keep evidence type visible. Do not present preprints as peer reviewed. Publication-type exclusions should be explicit. If reviews are allowed for only one topic or tier, use a scoped exception instead of globally allowing them.

## Ranking and limits

The ordinary quota controls routine topics. An additive priority topic may exceed it. State this clearly in the generated profile and child skill. Overflow records must remain in a persistent pending queue rather than disappear when their date window expires.

## Failure semantics

One unavailable source must not suppress records retrieved from other sources. Save successfully sent items immediately, but do not write the complete-day marker until every configured source has succeeded. The fallback run then retries missing sources while sent history prevents duplicates.

