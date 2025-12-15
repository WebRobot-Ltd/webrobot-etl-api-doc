---
title: Price comparison & e-commerce (EL)
version: 1.0.0
description: "Οδηγός (EL) για aggregation προσφορών και product matching με EAN· pivot/σύγκριση τιμών downstream"
---

# Price comparison & e-commerce (EL)

Αυτός ο οδηγός δείχνει πώς να χτίσετε pipelines ETL για **price comparison** σε πολλαπλές e-commerce πηγές, με product matching μέσω **EAN**.

## Στόχος

- εξαγωγή offers (row-level) από πολλαπλές πηγές
- normalization EAN, τιμών και νομίσματος
- deduplication
- δημιουργία **matching table** (pivot by source) downstream σε Trino/Spark SQL

## Παράδειγμα pipeline (5 sites)

- File: `examples/pipelines/19-price-comparison-5-sites.yaml`

Output: **row-level offers** (μία γραμμή ανά offer ανά πηγή), έτοιμα για pivot ανά EAN.

## Matching logic (EAN)

1. **Normalize**: αφαίρεση μη-ψηφίων, basic validation EAN-13
2. **Stable key**: `ean_normalized` ως primary matching key
3. **Fallback**: όταν λείπει EAN, χρήση `product_name_normalized` + επιπλέον κλειδιά (SKU/brand) με ελεγχόμενους κανόνες

## Matching table (downstream)

Παράδειγμα Trino pivot query για matching table ανά EAN:

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

## Συμμόρφωση

Χρησιμοποιήστε μόνο πηγές που επιτρέπεται να εξάγετε/καταναλώσετε (ToS/licenses). Όπου είναι δυνατό, προτιμήστε licensed feeds/APIs.


