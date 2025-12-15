---
title: Portfolio management & 90ήμερη πρόβλεψη asset (EL)
version: 1.0.0
description: "Οδηγός (EL) για κατασκευή training set 90 ημερών και fine-tuning τοπικού LLM (NVIDIA DGX SPARK)"
---

# Portfolio management & 90ήμερη πρόβλεψη asset (EL)

Use case για το layer **portfolio management** (Feeless): κατασκευή **training set** για πρόβλεψη 90 ημερών ενός target asset, με output έτοιμο για fine-tuning τοπικού LLM (π.χ. NVIDIA DGX SPARK).

## Στόχος

- multi-source signals (prices, macro, news/sentiment, alternative data)
- feature engineering (technical indicators, volatility, returns)
- target generation 90 ημερών (forward return)
- export dataset (CSV) με `instruction`, `input`, `output` + features/targets

## Παράδειγμα pipeline

- File: `examples/pipelines/24-portfolio-management-90d-prediction.yaml`

Σημείωση: για compliance/ToS, το παράδειγμα υποθέτει **social sentiment** ως licensed CSV feed (`${SOCIAL_SENTIMENT_DAILY_CSV_PATH}`), όχι απευθείας scraping από social.

## Output & post-processing

Το ETL εξάγει CSV· μετατροπή σε JSONL/Parquet (αν χρειάζεται) γίνεται downstream (Spark/Trino ή training tooling).


