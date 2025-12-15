---
title: Price comparison & e-commerce (IT)
version: 1.0.0
description: "Guida (IT) per aggregare offerte e costruire matching prodotti con EAN; pivot e confronto prezzi downstream"
---

# Price comparison & e-commerce (IT)

Questa guida mostra come costruire pipeline ETL per **price comparison** su più fonti e-commerce, con matching prodotto basato su **EAN**.

## Obiettivo

- estrarre offerte (row-level) da più fonti
- normalizzare EAN, prezzi e valuta
- deduplicare
- costruire la **tabella di matching** (pivot by source) downstream in Trino/Spark SQL

## Esempio pipeline (5 siti)

- File: `examples/pipelines/19-price-comparison-5-sites.yaml`

Output: **offerte row-level** (una riga per offerta per sorgente), pronte per il pivot per EAN.

## Matching logic (EAN)

1. **Normalizza**: rimuovi caratteri non numerici, valida EAN-13
2. **Key stabile**: usa `ean_normalized` come chiave primaria di matching
3. **Fallback**: se EAN manca, usa `product_name_normalized` + altri attributi (SKU/brand) con regole controllate

## Tabella di matching (downstream)

Esempio Trino pivot per ottenere un “matching table” per EAN:

```sql
SELECT
  ean_normalized AS ean,
  max_by(product_name, length(product_name)) AS product_name_canonical,
  min(CASE WHEN source = 'source_a' THEN price_numeric END) AS price_source_a,
  min(CASE WHEN source = 'source_b' THEN price_numeric END) AS price_source_b,
  min(CASE WHEN source = 'source_c' THEN price_numeric END) AS price_source_c,
  min(CASE WHEN source = 'source_d' THEN price_numeric END) AS price_source_d,
  min(CASE WHEN source = 'source_e' THEN price_numeric END) AS price_source_e,
  min(price_numeric) AS best_price,
  count(*) AS offers_count
FROM offers
WHERE ean_normalized IS NOT NULL
GROUP BY 1;
```

## Compliance

Usa solo fonti che puoi legittimamente estrarre/consultare (ToS/licenze). Dove possibile, preferisci feed/API licenziati.


