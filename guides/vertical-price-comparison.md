---
title: Price Comparison & E-commerce Vertical
version: 1.0.0
description: "Complete guide for building price comparison and e-commerce aggregation pipelines"
---

# Price Comparison & E-commerce Vertical

This guide demonstrates how to build **production-ready price comparison pipelines** that aggregate product offers from multiple e-commerce sources, normalize prices, and track availability.

## Business Use Case

**Goal**: Build a unified product catalog by aggregating offers from multiple e-commerce sites, enabling:

- **Price comparison**: Compare prices for the same product across sources
- **Availability tracking**: Monitor stock levels and availability
- **Price history**: Track price changes over time
- **Product matching**: Match products across sources using EAN, SKU, or other identifiers

## Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Source A   │     │  Source B   │     │  Source C   │
│  (Crawl)    │     │  (API)      │     │  (Search)   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Union &   │
                    │  Deduplicate│
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Normalize  │
                    │   Schema    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Enrich    │
                    │  (EAN, etc) │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Save to    │
                    │   Storage   │
                    └─────────────┘
```

## Pipeline Patterns

> **Important**: When starting a pipeline with crawling stages (`explore`, `join`, etc.), you **must** include a `fetch:` section with a starting URL. Pipelines that start with `load_csv` or other non-crawling stages don't require `fetch:`.

### Pattern 1: Multi-Source Union (Single Pipeline)

Use in-memory branching to combine multiple sources in a single pipeline:

```yaml
# Complete example: Multi-source price aggregation
fetch:
  url: "https://books.toscrape.com"  # Starting URL for Source A

pipeline:
  # ============================================
  # Source A: Direct crawl
  # ============================================
  - stage: explore
    args: [ "li.next a", 2 ]
  - stage: join
    args: [ "article.product_pod h3 a", "LeftOuter" ]
  - stage: extract
    args:
      - { selector: "h1", method: "text", as: "title" }
      - { selector: ".price_color", method: "text", as: "price_raw" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
      - { selector: "meta[property='product:ean']", method: "attr:content", as: "ean" }
  - stage: cache
    args: []
  - stage: store
    args: [ "source_a_offers" ]

  # ============================================
  # Source B: API-based discovery
  # ============================================
  - stage: reset
    args: []
  - stage: load_csv
    args:
      - { path: "${INPUT_CSV_PATH}", header: "true", inferSchema: "true" }
  - stage: searchEngine
    args:
      - provider: "google"
        ean: "$ean"
        num_results: 5
        enrich: true
  - stage: visit
    args: [ "$result_link" ]
  - stage: extract
    args:
      - { selector: "title", method: "text", as: "title" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
      - { selector: "meta[property='product:price:amount']", method: "attr:content", as: "price_raw" }
      - { selector: "meta[property='product:ean']", method: "attr:content", as: "ean" }
  - stage: cache
    args: []
  - stage: store
    args: [ "source_b_offers" ]

  # ============================================
  # Merge: Union all sources
  # ============================================
  - stage: reset
    args: []
  - stage: union_with
    args: [ "source_a_offers", "source_b_offers" ]

  # ============================================
  # Deduplication by EAN (if available) or URL
  # ============================================
  - stage: dedup
    args: [ "ean", "url" ]  # Deduplicate by EAN first, then URL

  # ============================================
  # Normalize prices and schema
  # ============================================
  - stage: python_row_transform:normalize_price
    args: []

  # ============================================
  # Save final result
  # ============================================
  - stage: save_csv
    args: [ "${OUTPUT_PATH_STITCHED}", "overwrite" ]
```

**File**: [`examples/pipelines/17-single-pipeline-multi-source-union.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/17-single-pipeline-multi-source-union.yaml)

### Pattern 2: Separate Pipelines with Stitching

Run separate pipelines for each source, then stitch outputs:

**Source A Pipeline**:
```yaml
# Source A: Direct crawl
fetch:
  url: "https://books.toscrape.com"

pipeline:
  - stage: explore
    args: [ "li.next a", 2 ]
  - stage: join
    args: [ "article.product_pod h3 a", "LeftOuter" ]
  - stage: extract
    args:
      - { selector: "h1", method: "text", as: "title" }
      - { selector: ".price_color", method: "text", as: "price_raw" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
  - stage: save_csv
    args: [ "${OUTPUT_PATH_A}", "overwrite" ]
```

**Source B Pipeline**:
```yaml
# Source B: API-based discovery
pipeline:
  - stage: load_csv
    args:
      - { path: "${INPUT_CSV_PATH}", header: "true", inferSchema: "true" }
  - stage: searchEngine
    args:
      - provider: "google"
        ean: "$ean"
        num_results: 5
        enrich: true
  - stage: visit
    args: [ "$result_link" ]
  - stage: extract
    args:
      - { selector: "title", method: "text", as: "title" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
      - { selector: "meta[property='product:price:amount']", method: "attr:content", as: "price_raw" }
  - stage: save_csv
    args: [ "${OUTPUT_PATH_B}", "overwrite" ]
```

**Stitching Pipeline**:
```yaml
# Stitching: Union and deduplicate
pipeline:
  - stage: load_union
    args:
      - { format: "csv", path: "${OUTPUT_PATH_A}", options: { header: "true", inferSchema: "true" } }
      - { format: "csv", path: "${OUTPUT_PATH_B}", options: { header: "true", inferSchema: "true" } }
  - stage: dedup
    args: [ "url" ]
  - stage: save_csv
    args: [ "${OUTPUT_PATH_STITCHED}", "overwrite" ]
```

**Files**:
- Source A: [`examples/pipelines/11-vertical-source-a-offers.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/11-vertical-source-a-offers.yaml)
- Source B: [`examples/pipelines/12-vertical-source-b-offers.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/12-vertical-source-b-offers.yaml)
- Stitching: [`examples/pipelines/13-vertical-stitch-union-dedup-offers.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/13-vertical-stitch-union-dedup-offers.yaml)

## Canonical Schema

Define a **canonical schema** that all sources map to:

```yaml
# Canonical product offer schema
fields:
  - title: string          # Product title
  - price: decimal        # Normalized price (same currency)
  - price_raw: string     # Original price string (for debugging)
  - currency: string      # Currency code (EUR, USD, etc.)
  - url: string          # Product page URL
  - ean: string          # EAN-13 barcode (if available)
  - sku: string          # SKU (if available)
  - availability: string # "in_stock", "out_of_stock", "preorder"
  - source: string       # Source identifier (e.g., "amazon", "ebay")
  - image_url: string    # Product image URL
  - description: string  # Product description
  - brand: string       # Brand name
  - category: string    # Product category
```

## Price Normalization

Normalize prices to a common currency and format:

```python
# Python extension: normalize_price
def normalize_price(row):
    import re
    from decimal import Decimal
    
    price_raw = row.get("price_raw", "")
    currency = row.get("currency", "EUR")
    
    # Extract numeric value
    price_match = re.search(r'[\d,]+\.?\d*', price_raw.replace(',', ''))
    if price_match:
        price_value = Decimal(price_match.group())
        
        # Convert to EUR if needed (simplified example)
        if currency == "USD":
            price_value = price_value * Decimal("0.92")  # Example rate
            currency = "EUR"
        
        return {
            **row,
            "price": float(price_value),
            "currency": currency,
            "price_normalized": True
        }
    
    return {**row, "price": None, "price_normalized": False}
```

## EAN-Based Product Matching

Use EAN codes for accurate product matching across sources:

```yaml
# EAN enrichment pipeline
pipeline:
  - stage: load_csv
    args:
      - { path: "${INPUT_CSV_PATH}", header: "true", inferSchema: "true" }
  - stage: searchEngine
    args:
      - provider: "google"
        ean: "$EAN number"
        num_results: 10
        image_search: true
        enrich: true
        as: "search_json"
  - stage: visit
    args: [ "$result_link" ]
  - stage: iextract
    args:
      - "Extract: product name, brand, price, EAN if visible, and all product image URLs"
      - "prod_"
  - stage: enrichMatchingScore
    args: [ { input_ean_field: "EAN number", iextract_prefix: "prod_" } ]
  - stage: save_csv
    args: [ "${OUTPUT_PATH}", "overwrite" ]
```

**File**: [`examples/pipelines/07-searchengine-ean-enrich.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/07-searchengine-ean-enrich.yaml)

## Deduplication Strategy

Choose deduplication keys based on data quality:

### Strategy 1: EAN-Based (Best)

If EAN codes are available and reliable:

```yaml
- stage: dedup
  args: [ "ean" ]  # Deduplicate by EAN
```

### Strategy 2: URL-Based (Fallback)

If EAN is not available:

```yaml
- stage: dedup
  args: [ "url" ]  # Deduplicate by URL
```

### Strategy 3: Multi-Key (Robust)

Combine multiple keys for better accuracy:

```yaml
- stage: dedup
  args: [ "ean", "url", "source" ]  # Deduplicate by EAN, then URL, then source
```

## Price Comparison Analysis

After aggregation, analyze price differences:

```sql
-- Query via Trino (after pipeline execution)
SELECT 
    ean,
    title,
    MIN(price) as min_price,
    MAX(price) as max_price,
    AVG(price) as avg_price,
    COUNT(*) as offer_count,
    MAX(price) - MIN(price) as price_range
FROM stitched_offers
WHERE ean IS NOT NULL
GROUP BY ean, title
HAVING COUNT(*) > 1
ORDER BY price_range DESC
LIMIT 100;
```

## Best Practices

### 1. Use Environment Variables

Always use environment variables for paths:

```yaml
- stage: save_csv
  args: [ "${OUTPUT_PATH}", "overwrite" ]
```

### 2. Cache Before Store

Cache intermediate results before storing branches:

```yaml
- stage: cache
  args: []
- stage: store
  args: [ "branch_label" ]
```

### 3. Normalize Early

Normalize prices and schemas as early as possible:

```yaml
- stage: extract
  args: [ ... ]
- stage: python_row_transform:normalize_price
  args: []
```

### 4. Validate EAN Codes

Validate EAN codes before using them for matching:

```python
def validate_ean(ean):
    if not ean or len(ean) not in [8, 13]:
        return False
    # Add checksum validation
    return True
```

### 5. Handle Missing Data

Handle missing fields gracefully:

```yaml
- stage: extract
  args:
    - { selector: "h1", method: "text", as: "title", default: "Unknown" }
    - { selector: ".price_color", method: "text", as: "price_raw", default: "0.00" }
```

## Related Documentation

- **[Vertical Use Cases](vertical-use-cases.md)**: Overview of all vertical use cases
- **[Build a Pipeline](build-a-pipeline.md)**: Learn pipeline fundamentals
- **[Pipeline Stages Reference](pipeline-stages.md)**: Complete stage reference
- **[EAN Image Sourcing Plugin](ean-image-sourcing.md)**: EAN-based product matching

