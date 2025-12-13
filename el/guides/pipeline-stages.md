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

## Plugin EAN

Αν χρησιμοποιείτε το plugin EAN: δείτε [EAN Image Sourcing (EL)](ean-image-sourcing.md) για stage-set και CloudCredential injection.

