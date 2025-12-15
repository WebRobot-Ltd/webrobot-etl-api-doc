---
title: Real estate arbitrage & clustering (IT)
version: 1.0.0
description: "Guida (IT) per aggregare annunci immobiliari, fare entity resolution via clustering e calcolare segnali di arbitraggio downstream"
---

# Real estate arbitrage & clustering (IT)

Questo verticale mostra come:

- aggregare annunci da più portali
- normalizzare indirizzi e calcolare feature (es. `price_per_sqm`)
- clusterizzare con `propertyCluster` per identificare immobili “simili/uguali”
- calcolare arbitraggio usando statistiche di cluster e fonti esterne (downstream)

## Esempio pipeline

- File: `examples/pipelines/22-real-estate-arbitrage-clustering.yaml`

## Post-clustering (downstream)

La fase di analisi cluster (media, deviazione, outlier) è consigliata downstream in Trino/Spark SQL.


