---
title: Vertical Use Cases
version: 1.0.0
description: "Industry-specific use cases and complete pipeline examples for vertical markets"
---

# Vertical Use Cases

This section provides **complete, production-ready examples** for specific industry verticals, demonstrating how to build end-to-end data pipelines using WebRobot ETL.

## What are Vertical Use Cases?

Vertical use cases are **industry-specific data pipelines** that solve real business problems:

- **Price Comparison & E-commerce**: Aggregate product offers from multiple sources, compare prices, track availability
- **Real Estate**: Monitor property listings, track price trends, identify arbitrage opportunities
- **Sports Betting**: Collect odds from multiple bookmakers, detect arbitrage opportunities, track line movements
- **Financial Markets**: Aggregate news, earnings transcripts, social sentiment for trading signals
- **Legal & Compliance**: Monitor regulatory changes, extract contract terms, track compliance deadlines
- **Healthcare**: Aggregate clinical guidelines, drug information, medical research

## Common Patterns Across Verticals

> **Important**: When starting a pipeline with crawling stages (`explore`, `join`, etc.), you **must** include a `fetch:` section with a starting URL. Pipelines that start with `load_csv` or other non-crawling stages don't require `fetch:`.

### 1. Multi-Source Aggregation

Most verticals require aggregating data from **multiple sources**:

```yaml
# Pattern: Fetch from multiple sources, union, deduplicate
fetch:
  url: "https://example.com"  # Starting URL for Source A

pipeline:
  # Source A: Direct crawl
  - stage: explore
    args: [ "li.next a", 2 ]
  - stage: join
    args: [ "article.product_pod h3 a", "LeftOuter" ]
  - stage: extract
    args:
      - { selector: "h1", method: "text", as: "title" }
      - { selector: ".price_color", method: "text", as: "price_raw" }
  - stage: cache
    args: []
  - stage: store
    args: [ "source_a" ]

  # Source B: API-based discovery
  - stage: reset
    args: []
  - stage: load_csv
    args:
      - { path: "${INPUT_PATH}", header: "true", inferSchema: "true" }
  - stage: searchEngine
    args:
      - provider: "google"
        ean: "$ean"
        num_results: 5
  - stage: visit
    args: [ "$result_link" ]
  - stage: extract
    args:
      - { selector: "title", method: "text", as: "title" }
      - { selector: "meta[property='product:price:amount']", method: "attr:content", as: "price_raw" ]
  - stage: cache
    args: []
  - stage: store
    args: [ "source_b" ]

  # Merge sources
  - stage: reset
    args: []
  - stage: union_with
    args: [ "source_a", "source_b" ]
  - stage: dedup
    args: [ "url" ]  # or "ean", "sku", etc.
```

### 2. Entity Resolution & Deduplication

Use **stable business keys** for deduplication:

- **E-commerce**: `ean`, `sku`, `url` + `source`
- **Real Estate**: `property_id`, `address` + `source`
- **Sports Betting**: `match_id`, `bookmaker` + `market_type`
- **Financial**: `ticker`, `date`, `source`

### 3. Schema Normalization

Normalize data across sources to a **canonical schema**:

```yaml
# Example: Price normalization
- stage: python_row_transform:normalize_price
  args: []
```

### 4. Enrichment & Validation

Enrich records with additional data:

- **EAN validation**: Verify product codes
- **Geocoding**: Convert addresses to coordinates
- **Sentiment analysis**: Analyze text content
- **Image matching**: Match product images

## Vertical-Specific Guides

### 📦 [Price Comparison & E-commerce](vertical-price-comparison.md)

**Use Case**: Aggregate product offers from multiple e-commerce sites, compare prices, track availability.

**Key Features**:
- Multi-source product aggregation
- Price normalization and comparison
- EAN-based product matching
- Availability tracking
- Historical price analysis

**Example Output**: Unified product catalog with prices from 10+ sources, deduplicated by EAN.

---

### 🏠 [Real Estate](vertical-real-estate.md)

**Use Case**: Monitor property listings, track price trends, identify undervalued properties.

**Key Features**:
- Multi-listing site aggregation
- Price per square meter calculation
- Property clustering (ML-based)
- Arbitrage opportunity detection
- Market trend analysis

**Example Output**: Properties flagged as "undervalued" based on cluster analysis.

---

### ⚽ [Sports Betting](vertical-sports-betting.md)

**Use Case**: Collect odds from multiple bookmakers, detect arbitrage opportunities, track line movements.

**Key Features**:
- Multi-bookmaker odds aggregation
- Real-time odds polling
- Arbitrage detection (surebet scanner)
- Line movement tracking
- Implied probability calculation

**Example Output**: Arbitrage opportunities with profit margins > 2%.

---

### 📈 [Financial Markets](vertical-financial-markets.md)

**Use Case**: Aggregate news, earnings transcripts, social sentiment for trading signals.

**Key Features**:
- News aggregation (Bloomberg, Reuters, FT)
- Earnings call transcript extraction
- Social sentiment analysis (Twitter, Reddit)
- SEC filing extraction
- Trading signal generation

**Example Output**: Trading signals based on sentiment + news correlation.

---

### ⚖️ [Legal & Compliance](vertical-legal-compliance.md)

**Use Case**: Monitor regulatory changes, extract contract terms, track compliance deadlines.

**Key Features**:
- Regulatory document monitoring
- Contract clause extraction
- Obligation tracking
- Compliance deadline alerts
- Risk flagging

**Example Output**: Compliance dashboard with upcoming deadlines.

---

### 🏥 [Healthcare](vertical-healthcare.md)

**Use Case**: Aggregate clinical guidelines, drug information, medical research.

**Key Features**:
- Clinical guideline aggregation
- Drug interaction checking
- Medical research paper extraction
- Patient data anonymization
- Regulatory compliance

**Example Output**: Drug interaction database with clinical evidence.

## Getting Started

1. **Choose your vertical**: Review the guides above to find the use case that matches your needs
2. **Review the architecture**: Each guide includes a complete pipeline architecture
3. **Customize the pipeline**: Adapt the YAML examples to your specific sources and requirements
4. **Deploy and monitor**: Use the WebRobot API to deploy and monitor your pipelines

## Best Practices

### 1. Start with a Single Source

Begin with one source, validate the extraction, then add more sources:

```yaml
# Phase 1: Single source
fetch:
  url: "https://example.com"  # Starting URL

pipeline:
  - stage: explore
    args: [ "li.next a", 2 ]
  - stage: extract
    args: [ ... ]
  - stage: save_csv
    args: [ "${OUTPUT_PATH}", "overwrite" ]
```

### 2. Use Environment Variables

Always use environment variables for paths and configuration:

```yaml
- stage: save_csv
  args: [ "${OUTPUT_PATH}", "overwrite" ]
```

### 3. Cache Intermediate Results

Use `cache` or `persist` before `store` for in-memory branching:

```yaml
- stage: cache
  args: []
- stage: store
  args: [ "branch_label" ]
```

### 4. Choose Stable Deduplication Keys

Select keys that uniquely identify entities across sources:

- ✅ Good: `ean`, `sku`, `property_id`, `match_id`
- ❌ Bad: `title`, `description`, `price`

### 5. Normalize Schemas Early

Normalize data as early as possible in the pipeline:

```yaml
- stage: extract
  args: [ ... ]
- stage: python_row_transform:normalize_schema
  args: []
```

## Related Documentation

- **[Build a Pipeline](build-a-pipeline.md)**: Learn the fundamentals of building pipelines
- **[Pipeline Stages Reference](pipeline-stages.md)**: Complete reference of available stages
- **[Pipeline Examples](pipeline-examples.md)**: Generic pipeline examples
- **[Observability & Metrics](observability-metrics.md)**: Monitor your vertical pipelines

