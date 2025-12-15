---
title: Sports betting & odds (EL)
version: 1.0.0
description: "Οδηγός (EL) για odds aggregation, event matching και row-level export για surebet detection downstream"
---

# Sports betting & odds (EL)

Αυτός ο οδηγός δείχνει πώς να χτίσετε pipelines για:

- εξαγωγή odds από πολλαπλούς bookmakers
- normalization και event matching (`event_id`)
- export **row-level** odds για surebet υπολογισμό downstream (Trino/Spark SQL)

## Pipeline examples

- Odds aggregation (5 bookmakers, placeholder/compliance): `examples/pipelines/20-sports-betting-5-bookmakers.yaml`
- Surebet με intelligent extraction: `examples/pipelines/21-surebet-intelligent-extraction.yaml`

## Event matching (κρίσιμο)

Επειδή το ίδιο event μπορεί να έχει διαφορετικά ονόματα ανά πλατφόρμα:

- normalize `event_name` (lowercase, team mappings, καθαρισμός)
- normalize/parse `event_date`
- δημιουργία σταθερού `event_id` από (`event_name_normalized`, `event_date`)
- `matching_key = event_id + market_type + selection` για downstream aggregation

## Surebet detection (downstream)

Ο surebet υπολογισμός απαιτεί pivot/aggregation ανά `(event_id, market_type, selection)` across bookmakers. Το ETL εξάγει row-level odds· το pivot και η surebet μαθηματική γίνονται downstream.


