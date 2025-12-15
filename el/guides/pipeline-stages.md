---
title: Αναφορά stages pipeline (EL)
version: 1.0.0
description: Αναφορά των κύριων stages και σημειώσεις για επεκτάσεις/resolver/actions
---

# Αναφορά stages pipeline (EL)

[English version](../../guides/pipeline-stages.md) | [Versione italiana](../../it/guides/pipeline-stages.md)

Αυτή η σελίδα συνοψίζει τις βασικές έννοιες. Για τη λεπτομερή ανάλυση "stage προς stage" (όλα τα args και οι περιπτώσεις), χρησιμοποιήστε την αγγλική έκδοση.

## Σημαντικές σημειώσεις για τον parser YAML

- Κάθε στοιχείο στο `pipeline:` πρέπει να έχει **μόνο**:
  - `stage` (string)
  - `args` (προαιρετικός πίνακας)
- Επιπλέον κλειδιά στο stage (π.χ. `name`, `when`) **δεν υποστηρίζονται** από τον parser Scala.

### Σημείωση για `fetch:` (σημαντικό)

Όταν ένα pipeline ξεκινά με crawling stages (`explore`, `join`, `visitExplore`, `visitJoin`, κ.λπ.) πρέπει πάντα να υπάρχει top-level `fetch:` με URL εκκίνησης.

## Join: wget vs visit

- `join`: χρησιμοποιεί HTTP trace από προεπιλογή (wget-like).
- `visitJoin`: χρησιμοποιεί browser/Visit (plugin).
- `wgetJoin`: ρητός wrapper για `FetchedDataset.wgetJoin`.

## Intelligent stages + caching selectors (RoadRunner)

Τα "έξυπνα" stages που συμπεραίνουν selectors (π.χ. `intelligentFlatSelect`, `iextract`) χρησιμοποιούν:
- fingerprint του template (cluster),
- cache για `(cluster, prompt)`,
- pre-population με RoadRunner για σταθεροποίηση wrapper/selector και μείωση επαναλαμβανόμενων συμπερασμάτων.

## Stages που χρησιμοποιούνται συχνά (παραδείγματα)

```yaml
pipeline:
  - stage: searchEngine
    args:
      - provider: "google"
        ean: "$EAN number"
        num_results: 10
  - stage: visit
    args: [ "$result_link" ]
  - stage: iextract
    args: [ "Extract fields...", "prod_" ]
```

## Utility και σύνθεση πολλαπλών πηγών

### `cache`

Αποθήκευση/persist του τρέχοντος dataset (Spark `.cache()`).

```yaml
pipeline:
  - stage: cache
    args: []
```

### `store` / `reset` / `union_with`

Helpers του runner για σύνθεση multi-source pipelines μέσα στο ίδιο YAML:

- `store`: αποθηκεύει το τρέχον dataset με label
- `reset`: ξεκινάει “blank” dataset
- `union_with`: ενώνει το τρέχον dataset με ένα/περισσότερα αποθηκευμένα branches

```yaml
pipeline:
  - stage: visit
    args: [ "https://example.com" ]
  - stage: extract
    args:
      - { selector: "h1", method: "text", as: "title" }
  - stage: store
    args: [ "a" ]

  - stage: reset
    args: []
  - stage: load_csv
    args:
      - { path: "${SOURCE_B_CSV}", header: "true", inferSchema: "true" }
  - stage: store
    args: [ "b" ]

  - stage: reset
    args: []
  - stage: union_with
    args: [ "a", "b" ]
  - stage: dedup
    args: [ "url" ]
```

### `propertyCluster`

Stage (plugin) για unsupervised clustering (real estate). Δείτε τον οδηγό real estate για το use case.

## Plugin EAN

Αν χρησιμοποιείτε το plugin EAN: δείτε [EAN Image Sourcing (EL)](ean-image-sourcing.md) για stage-set και CloudCredential injection.

