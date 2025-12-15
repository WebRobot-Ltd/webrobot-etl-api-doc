---
title: Κάθετα use cases (EL)
version: 1.0.0
description: "Κάθετα use cases και πλήρεις οδηγοί στα ελληνικά, ευθυγραμμισμένοι με τα YAML examples στο repository"
---

# Κάθετα use cases (EL)

Αυτή η ενότητα συγκεντρώνει **κάθετα use cases** (end-to-end) και συνδέει τους αντίστοιχους οδηγούς στα ελληνικά. Τα runnable YAML παραδείγματα βρίσκονται στο `examples/pipelines/`.

## Σημείωση για crawling (`fetch:`)

> Αν ένα pipeline ξεκινά με crawling stages (`explore`, `join`, `visitExplore`, `visitJoin`, κ.λπ.) πρέπει πάντα να υπάρχει top-level `fetch:` με αρχικό URL.

## Κοινά patterns

- **Multi-source**: πολλαπλά branches (crawl/API/CSV), έπειτα ένωση με `store`/`reset`/`union_with` και dedup με `dedup`.
- **Entity resolution**: σταθερά business keys (EAN για προϊόντα, `event_id` για events, `cluster_id` για ακίνητα).
- **Normalization**: ενοποίηση schema/τιμών πριν τη σύγκριση.
- **Aggregations/pivot**: οι τελικοί πίνακες matching προτείνονται downstream σε **Trino/Spark SQL**, κρατώντας το ETL row-level.

## Διαθέσιμοι κάθετοι οδηγοί (EL)

- **[Price Comparison & E-commerce (EL)](vertical-price-comparison.md)**
- **[Sports Betting & Odds (EL)](vertical-sports-betting.md)**
- **[Real Estate Arbitrage (EL)](vertical-real-estate.md)**
- **[Dataset Fine-tuning LLM (EL)](vertical-llm-finetuning.md)** (policy **No-CC**)
- **[Portfolio Management & 90ήμερη Πρόβλεψη (EL)](vertical-portfolio-management.md)**


