---
title: Sports betting & odds (IT)
version: 1.0.0
description: "Guida (IT) per aggregare odds, fare event matching e preparare dataset row-level per surebet detection downstream"
---

# Sports betting & odds (IT)

Questa guida mostra come costruire pipeline per:

- estrarre odds da più bookmaker
- normalizzare e fare matching evento (`event_id`)
- esportare odds **row-level** per calcolo surebet downstream (Trino/Spark SQL)

## Esempi pipeline

- Odds aggregation (5 bookmaker, placeholder/compliance): `examples/pipelines/20-sports-betting-5-bookmakers.yaml`
- Surebet con estrazione intelligente: `examples/pipelines/21-surebet-intelligent-extraction.yaml`

## Event matching (cruciale)

Poiché lo stesso evento può avere nomi diversi tra piattaforme:

- normalizza `event_name` (lowercase, mapping team, rimozione rumore)
- normalizza/parse `event_date`
- genera `event_id` stabile da (`event_name_normalized`, `event_date`)
- usa `matching_key = event_id + market_type + selection` per aggregare

## Surebet detection (downstream)

Il calcolo surebet richiede pivot/aggregazione per `(event_id, market_type, selection)` su più bookmaker. L’ETL esporta row-level odds; la tabella di confronto e la matematica surebet vanno fatte downstream.


