---
title: Portfolio management & previsione asset a 90 giorni (IT)
version: 1.0.0
description: "Guida (IT) per costruire training set per previsione 90 giorni e fine-tuning LLM locale (NVIDIA DGX SPARK)"
---

# Portfolio management & previsione asset a 90 giorni (IT)

Use case per il layer di **portfolio management** (progetto Feeless): costruire un **training set** per predire a 90 giorni un asset target, con output pronto per fine-tuning di un LLM locale (es. su NVIDIA DGX SPARK).

## Obiettivo

- aggregare segnali multi-sorgente (prezzi, macro, news/sentiment, alternative data)
- costruire feature (indicatori tecnici, volatilità, ritorni)
- calcolare target a 90 giorni (forward return)
- esportare dataset (CSV) con colonne `instruction`, `input`, `output` + feature/target

## Esempio pipeline

- File: `examples/pipelines/24-portfolio-management-90d-prediction.yaml`

Nota: per compliance e ToS, l’esempio assume il **social sentiment** come feed licenziato in CSV (`${SOCIAL_SENTIMENT_DAILY_CSV_PATH}`), non scraping diretto da social.

## Output e post-processing

L’ETL esporta CSV; la conversione a JSONL/Parquet (se richiesta dal training stack) è un pass downstream (Spark/Trino o tooling di training).


