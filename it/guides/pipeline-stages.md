---
title: Riferimento stage pipeline (IT)
version: 1.0.0
description: Riferimento dei principali stage e note su estensioni/resolver/actions
---

# Riferimento stage pipeline (IT)

[English version](../../guides/pipeline-stages.md)

Questa pagina riassume i concetti chiave. Per il dettaglio “stage per stage” (tutti gli args e i casi), usa la versione inglese.

## Note importanti sul parser YAML

- Ogni elemento in `pipeline:` deve avere **solo**:
  - `stage` (string)
  - `args` (array opzionale)
- Chiavi extra nello stage (es. `name`, `when`) **non sono supportate** dal parser Scala.

## Join: wget vs visit

- `join`: usa una trace HTTP di default (wget-like).
- `visitJoin`: usa browser/Visit (plugin).
- `wgetJoin`: wrapper esplicito per `FetchedDataset.wgetJoin`.

## Intelligent stages + caching selettori (RoadRunner)

Gli stage “intelligenti” che inferiscono selettori (es. `intelligentFlatSelect`, `iextract`) usano:
- fingerprint del template (cluster),
- cache per `(cluster, prompt)`,
- pre-population con RoadRunner per stabilizzare wrapper/selector e ridurre inferenze ripetute.

## Stage usati spesso (esempi)

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

Se usi il plugin EAN: vedi [EAN Image Sourcing (IT)](ean-image-sourcing.md) per stage-set e CloudCredential injection.


