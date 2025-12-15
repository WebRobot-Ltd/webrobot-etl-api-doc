---
title: Use case verticali (IT)
version: 1.0.0
description: "Use case verticali e guide complete in italiano, allineate agli esempi YAML nel repository"
---

# Use case verticali (IT)

Questa sezione raccoglie **use case verticali** (end-to-end) e collega alle guide in italiano, con esempi YAML reali sotto `examples/pipelines/`.

## Nota importante sul crawling (`fetch:`)

> Se una pipeline parte con stage di crawling (`explore`, `join`, `visitExplore`, `visitJoin`, ecc.) devi includere sempre un blocco top-level `fetch:` con una URL iniziale.

## Pattern comuni

- **Multi-sorgente**: esegui più rami (crawl/API/CSV), poi unisci con `store`/`reset`/`union_with` e deduplica con `dedup`.
- **Entity resolution**: definisci chiavi stabili (EAN per prodotti, `event_id` per eventi, `cluster_id` per immobili).
- **Normalizzazione**: uniforma schema e valori (prezzi, valute, nomi evento, indirizzi) prima di confrontare.
- **Aggregazioni/pivot**: per tabelle di matching finali, preferisci **Trino/Spark SQL** (downstream), mantenendo l’ETL row-level.

## Guide verticali disponibili (IT)

- **[Price Comparison & E-commerce (IT)](vertical-price-comparison.md)**
- **[Sports Betting & Odds (IT)](vertical-sports-betting.md)**
- **[Real Estate Arbitrage (IT)](vertical-real-estate.md)**
- **[Dataset Fine-tuning LLM (IT)](vertical-llm-finetuning.md)** (policy **No-CC**)
- **[Portfolio Management & Previsione 90 giorni (IT)](vertical-portfolio-management.md)**


