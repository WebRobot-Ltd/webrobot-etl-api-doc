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

### Nota su `fetch:` (importante)

Quando una pipeline inizia con stage di crawling (`explore`, `join`, `visitExplore`, `visitJoin`, ecc.) devi sempre includere un blocco top-level `fetch:` con una URL di partenza.

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

## Utility e composizione multi-sorgente

### `cache`

Persistenza del dataset corrente (Spark `.cache()`).

```yaml
pipeline:
  - stage: cache
    args: []
```

### `store` / `reset` / `union_with`

Helper del runner per comporre pipeline multi-sorgente nello stesso YAML:

- `store`: salva il dataset corrente con una label
- `reset`: riparte da un dataset vuoto
- `union_with`: unisce il dataset corrente con uno o più branch salvati

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

Stage (plugin) per clustering non supervisionato (real estate). Vedi guida real estate per il caso d’uso.

## Plugin EAN

Se usi il plugin EAN: vedi [EAN Image Sourcing (IT)](ean-image-sourcing.md) per stage-set e CloudCredential injection.


