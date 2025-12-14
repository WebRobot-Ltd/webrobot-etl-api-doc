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

## Concrete Example: Price Comparison Across 5 E-commerce Sites

This example demonstrates a **complete production pipeline** that aggregates product offers from 5 major e-commerce sites and generates a **product matching table** for price comparison.

### E-commerce Sites

1. **Amazon** - Direct crawl
2. **eBay** - Direct crawl  
3. **Walmart** - Direct crawl
4. **Target** - API-based (CSV input)
5. **Best Buy** - Direct crawl

### Complete Pipeline: Multi-Source Aggregation

```yaml
# Complete example: Price comparison across 5 e-commerce sites
fetch:
  url: "https://www.amazon.com/s?k=electronics"  # Starting URL for Amazon

pipeline:
  # ============================================
  # Site 1: Amazon (Direct crawl)
  # ============================================
  - stage: explore
    args: [ "a.s-pagination-next", 5 ]  # Navigate through search pages
  - stage: join
    args: [ "h2 a.a-link-normal", "LeftOuter" ]  # Click on product links
  - stage: extract
    args:
      - { selector: "span#productTitle", method: "text", as: "product_name" }
      - { selector: "span.a-price-whole", method: "text", as: "price_raw" }
      - { selector: "span.a-price-symbol", method: "text", as: "currency_symbol" }
      - { selector: "span#productEAN", method: "text", as: "ean" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
      - { selector: "img#landingImage", method: "attr:src", as: "image_url" }
  - stage: python_row_transform:normalize_amazon
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - source: "amazon.com"
  - stage: cache
    args: []
  - stage: store
    args: [ "amazon_offers" ]

  # ============================================
  # Site 2: eBay (Direct crawl)
  # ============================================
  - stage: reset
    args: []
  - stage: visit
    args: [ "https://www.ebay.com/sch/i.html?_nkw=electronics" ]
  - stage: explore
    args: [ "a.pagination__next", 5 ]
  - stage: join
    args: [ "h3.s-item__title a", "LeftOuter" ]
  - stage: extract
    args:
      - { selector: "h1#x-item-title-label", method: "text", as: "product_name" }
      - { selector: "span.notranslate", method: "text", as: "price_raw" }
      - { selector: "span.ux-textspans", method: "text", as: "currency_symbol" }
      - { selector: "div.ux-labels-values__values-content span", method: "text", as: "ean" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
      - { selector: "img#icImg", method: "attr:src", as: "image_url" }
  - stage: python_row_transform:normalize_ebay
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - source: "ebay.com"
  - stage: cache
    args: []
  - stage: store
    args: [ "ebay_offers" ]

  # ============================================
  # Site 3: Walmart (Direct crawl)
  # ============================================
  - stage: reset
    args: []
  - stage: visit
    args: [ "https://www.walmart.com/search?q=electronics" ]
  - stage: explore
    args: [ "a[data-testid='pagination-next']", 5 ]
  - stage: join
    args: [ "a[data-testid='product-title']", "LeftOuter" ]
  - stage: extract
    args:
      - { selector: "h1.prod-ProductTitle", method: "text", as: "product_name" }
      - { selector: "span.price-characteristic", method: "text", as: "price_raw" }
      - { selector: "span.price-currency", method: "text", as: "currency_symbol" }
      - { selector: "span[itemprop='gtin13']", method: "text", as: "ean" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
      - { selector: "img[data-testid='product-image']", method: "attr:src", as: "image_url" }
  - stage: python_row_transform:normalize_walmart
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - source: "walmart.com"
  - stage: cache
    args: []
  - stage: store
    args: [ "walmart_offers" ]

  # ============================================
  # Site 4: Target (API-based - CSV input)
  # ============================================
  - stage: reset
    args: []
  - stage: load_csv
    args:
      - { path: "${TARGET_API_RESPONSE_PATH}", header: "true", inferSchema: "true" }
  - stage: python_row_transform:normalize_target
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - source: "target.com"
  - stage: cache
    args: []
  - stage: store
    args: [ "target_offers" ]

  # ============================================
  # Site 5: Best Buy (Direct crawl)
  # ============================================
  - stage: reset
    args: []
  - stage: visit
    args: [ "https://www.bestbuy.com/site/searchpage.jsp?st=electronics" ]
  - stage: explore
    args: [ "a[aria-label='Next page']", 5 ]
  - stage: join
    args: [ "h4.sku-title a", "LeftOuter" ]
  - stage: extract
    args:
      - { selector: "h1.heading-5", method: "text", as: "product_name" }
      - { selector: "div.priceView-customer-price span", method: "text", as: "price_raw" }
      - { selector: "span.currency-symbol", method: "text", as: "currency_symbol" }
      - { selector: "span[itemprop='gtin13']", method: "text", as: "ean" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
      - { selector: "img.product-image", method: "attr:src", as: "image_url" }
  - stage: python_row_transform:normalize_bestbuy
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - source: "bestbuy.com"
  - stage: cache
    args: []
  - stage: store
    args: [ "bestbuy_offers" ]

  # ============================================
  # Merge: Union all sources
  # ============================================
  - stage: reset
    args: []
  - stage: union_with
    args: [ "amazon_offers", "ebay_offers", "walmart_offers", "target_offers", "bestbuy_offers" ]

  # ============================================
  # Deduplication by EAN (if available) or URL
  # ============================================
  - stage: dedup
    args: [ "ean", "url" ]  # Prioritize EAN for matching, fallback to URL

  # ============================================
  # Price Normalization & Currency Conversion
  # ============================================
  - stage: python_row_transform:normalize_price
    args: []
  - stage: python_row_transform:convert_currency
    args:
      - target_currency: "USD"  # Convert all prices to USD

  # ============================================
  # Save unified offers dataset
  # ============================================
  - stage: save_csv
    args: [ "${OUTPUT_PATH_UNIFIED_OFFERS}", "overwrite" ]
```

### Python Extensions for Normalization

```python
# python_extensions:
#   stages:
#     normalize_amazon:
#       type: row_transform
#       function: |
def normalize_amazon(row):
    """Normalize Amazon product data."""
    price_raw = row.get("price_raw", "").replace(",", "").strip()
    currency_symbol = row.get("currency_symbol", "$")
    try:
        row["price_numeric"] = float(price_raw)
        row["currency"] = "USD" if currency_symbol == "$" else "EUR"
    except:
        row["price_numeric"] = None
    row["ean"] = row.get("ean", "").strip()
    return row

#     normalize_ebay:
#       type: row_transform
#       function: |
def normalize_ebay(row):
    """Normalize eBay product data."""
    price_raw = row.get("price_raw", "").replace("$", "").replace(",", "").strip()
    try:
        row["price_numeric"] = float(price_raw)
        row["currency"] = "USD"
    except:
        row["price_numeric"] = None
    return row

#     normalize_walmart:
#       type: row_transform
#       function: |
def normalize_walmart(row):
    """Normalize Walmart product data."""
    price_raw = row.get("price_raw", "").replace("$", "").replace(",", "").strip()
    try:
        row["price_numeric"] = float(price_raw)
        row["currency"] = "USD"
    except:
        row["price_numeric"] = None
    return row

#     normalize_target:
#       type: row_transform
#       function: |
def normalize_target(row):
    """Normalize Target API response."""
    row["price_numeric"] = float(row.get("price", 0))
    row["currency"] = row.get("currency", "USD")
    row["product_name"] = row.get("name", "")
    row["ean"] = row.get("gtin", "")
    return row

#     normalize_bestbuy:
#       type: row_transform
#       function: |
def normalize_bestbuy(row):
    """Normalize Best Buy product data."""
    price_raw = row.get("price_raw", "").replace("$", "").replace(",", "").strip()
    try:
        row["price_numeric"] = float(price_raw)
        row["currency"] = "USD"
    except:
        row["price_numeric"] = None
    return row

#     normalize_price:
#       type: row_transform
#       function: |
def normalize_price(row):
    """Final price normalization."""
    if not row.get("price_numeric"):
        price_raw = row.get("price_raw", "")
        # Try to extract numeric value
        import re
        numbers = re.findall(r'\d+\.?\d*', price_raw.replace(",", ""))
        if numbers:
            row["price_numeric"] = float(numbers[0])
    return row

#     convert_currency:
#       type: row_transform
#       function: |
def convert_currency(row, target_currency="USD"):
    """Convert prices to target currency (simplified - use real API in production)."""
    # In production, use a currency conversion API
    currency = row.get("currency", "USD")
    price = row.get("price_numeric", 0)
    
    # Simplified conversion rates (use real-time rates in production)
    rates = {"USD": 1.0, "EUR": 1.1, "GBP": 1.25}
    
    if currency != target_currency and currency in rates:
        row["price_numeric"] = price * rates[currency]
        row["currency"] = target_currency
    
    return row
```

## Product Matching Logic: Recognizing the Same Product Across Platforms

**Critical Challenge**: The same product can appear with **different structures and names** across different e-commerce platforms. The EAN (European Article Number) is the **primary reference key** for product matching, but it's not always available or correctly formatted.

### Product Matching Strategy

1. **Primary Key: EAN Code**
   - EAN-13 (13 digits) is the most reliable identifier
   - Normalize EAN: remove spaces, dashes, leading zeros
   - Validate EAN format (checksum validation)

2. **Fallback Matching** (when EAN is missing or invalid):
   - **Product Name Normalization**: Remove brand variations, standardize formatting
   - **SKU Matching**: Use SKU if available (less reliable, retailer-specific)
   - **URL Canonicalization**: Extract product ID from URL patterns
   - **Fuzzy Matching**: Use similarity algorithms on product names + brand

3. **Aggregation by EAN**: All price comparisons must be **aggregated by EAN code** to create a unified comparison table.

### EAN Normalization and Validation

```python
# python_extensions:
#   stages:
#     normalize_ean:
#       type: row_transform
#       function: |
def normalize_ean(row):
    """Normalize and validate EAN code."""
    ean_raw = row.get("ean", "").strip()
    
    # Remove spaces, dashes, and other separators
    ean_cleaned = ean_raw.replace(" ", "").replace("-", "").replace(".", "")
    
    # Remove leading zeros if present (EAN-13 should be 13 digits)
    ean_cleaned = ean_cleaned.lstrip("0")
    
    # Pad to 13 digits if needed
    if len(ean_cleaned) < 13:
        ean_cleaned = ean_cleaned.zfill(13)
    elif len(ean_cleaned) > 13:
        # Take last 13 digits if longer
        ean_cleaned = ean_cleaned[-13:]
    
    # Validate EAN-13 checksum
    if len(ean_cleaned) == 13 and ean_cleaned.isdigit():
        # EAN-13 checksum validation
        checksum = 0
        for i in range(12):
            digit = int(ean_cleaned[i])
            if i % 2 == 0:
                checksum += digit
            else:
                checksum += digit * 3
        check_digit = (10 - (checksum % 10)) % 10
        
        if check_digit == int(ean_cleaned[12]):
            row["ean_normalized"] = ean_cleaned
            row["ean_valid"] = True
        else:
            row["ean_normalized"] = ean_cleaned  # Keep even if checksum fails
            row["ean_valid"] = False
    else:
        row["ean_normalized"] = None
        row["ean_valid"] = False
    
    return row

#     normalize_product_name:
#       type: row_transform
#       function: |
def normalize_product_name(row):
    """Normalize product name for fuzzy matching when EAN is missing."""
    import re
    
    product_name = row.get("product_name", "").strip()
    
    # Remove common prefixes/suffixes
    product_name = re.sub(r'^(New|Used|Refurbished|Renewed)\s+', '', product_name, flags=re.IGNORECASE)
    product_name = re.sub(r'\s+(New|Used|Refurbished|Renewed)$', '', product_name, flags=re.IGNORECASE)
    
    # Normalize whitespace
    product_name = re.sub(r'\s+', ' ', product_name).strip()
    
    # Remove special characters but keep spaces
    product_name = re.sub(r'[^\w\s-]', '', product_name)
    
    # Convert to lowercase for comparison
    row["product_name_normalized"] = product_name.lower()
    
    return row
```

### Aggregation by EAN Code

Before price comparison, **aggregate all offers by EAN code**:

```yaml
# Pipeline: Aggregate offers by EAN for price comparison
pipeline:
  - stage: load_csv
    args:
      - { path: "${OUTPUT_PATH_UNIFIED_OFFERS}", header: "true", inferSchema: "true" }
  
  # Normalize EAN codes
  - stage: python_row_transform:normalize_ean
    args: []
  
  # Normalize product names (for fallback matching)
  - stage: python_row_transform:normalize_product_name
    args: []
  
  # Group by EAN to create product matching table
  # Use aggregation to collect prices from all sources
  - stage: aggregation_group_by_key
    args:
      - key_field: "ean_normalized"
        aggregations:
          - field: "price_numeric"
            type: "collect_list"
            as: "prices_by_source"
          - field: "source"
            type: "collect_list"
            as: "sources"
          - field: "url"
            type: "collect_list"
            as: "urls"
          - field: "product_name"
            type: "first"
            as: "product_name_canonical"
  
  # Create price comparison columns (pivot-like structure)
  - stage: python_row_transform:create_price_comparison_by_ean
    args: []
  
  # Calculate best price and price differences
  - stage: python_row_transform:calculate_best_price_by_ean
    args: []
  
  - stage: save_csv
    args: [ "${OUTPUT_PATH_PRICE_COMPARISON_BY_EAN}", "overwrite" ]
```

```python
# python_extensions:
#   stages:
#     create_price_comparison_by_ean:
#       type: row_transform
#       function: |
def create_price_comparison_by_ean(row):
    """Create price comparison columns grouped by EAN."""
    prices_by_source = row.get("prices_by_source", [])
    sources = row.get("sources", [])
    urls = row.get("urls", [])
    
    # Create columns for each source
    source_price_map = {}
    source_url_map = {}
    
    for i, source in enumerate(sources):
        source_clean = source.replace(".com", "").replace(".", "_")
        if i < len(prices_by_source) and prices_by_source[i]:
            source_price_map[f"price_{source_clean}"] = prices_by_source[i]
        if i < len(urls) and urls[i]:
            source_url_map[f"url_{source_clean}"] = urls[i]
    
    # Add price columns
    for key, value in source_price_map.items():
        row[key] = value
    
    # Add URL columns
    for key, value in source_url_map.items():
        row[key] = value
    
    row["sources_count"] = len(sources)
    
    return row

#     calculate_best_price_by_ean:
#       type: row_transform
#       function: |
def calculate_best_price_by_ean(row):
    """Calculate best price and price differences for products grouped by EAN."""
    sources = ["amazon", "ebay", "walmart", "target", "bestbuy"]
    prices = {}
    
    for source in sources:
        price_key = f"price_{source}"
        price = row.get(price_key)
        if price and price > 0:
            prices[source] = price
    
    if prices:
        best_source = min(prices, key=prices.get)
        best_price = prices[best_source]
        worst_price = max(prices.values())
        
        row["best_price"] = best_price
        row["best_source"] = best_source
        row["worst_price"] = worst_price
        row["price_difference"] = worst_price - best_price
        row["price_difference_pct"] = ((worst_price - best_price) / best_price * 100) if best_price > 0 else 0
        row["sources_count"] = len(prices)
    
    return row
```

## Product Matching Table Generation

After aggregating offers from all sources **by EAN code**, generate a **product matching table** that shows prices for the same product (identified by EAN) across all 5 sites.

### Step 1: Generate Product Matching Table

```yaml
# Pipeline: Generate product matching table
pipeline:
  - stage: load_csv
    args:
      - { path: "${OUTPUT_PATH_UNIFIED_OFFERS}", header: "true", inferSchema: "true" }
  
  # Group by EAN to create matching table
  # Use joinWithByName to create a pivot-like structure
  - stage: joinWithByName
    args:
      - joinType: "full"
        joinKeys: ["ean"]
        leftAlias: "amazon"
        rightAlias: "ebay"
  
  # Save matching table
  - stage: save_csv
    args: [ "${OUTPUT_PATH_MATCHING_TABLE}", "overwrite" ]
```

### Step 2: Create Pivot Table for Price Comparison

A more efficient approach is to use a Python transform to create a pivot table:

```yaml
# Pipeline: Create price comparison pivot table
pipeline:
  - stage: load_csv
    args:
      - { path: "${OUTPUT_PATH_UNIFIED_OFFERS}", header: "true", inferSchema: "true" }
  
  # Create pivot table grouped by EAN
  - stage: python_row_transform:create_price_comparison_table
    args: []
  
  - stage: save_csv
    args: [ "${OUTPUT_PATH_PRICE_COMPARISON_TABLE}", "overwrite" ]
```

```python
# python_extensions:
#   stages:
#     create_price_comparison_table:
#       type: row_transform
#       function: |
def create_price_comparison_table(row):
    """Create a price comparison table row for each EAN."""
    # This would typically be done as a groupBy operation
    # For now, we'll mark rows for later aggregation
    ean = row.get("ean", "")
    source = row.get("source", "")
    price = row.get("price_numeric", 0)
    
    # Create columns for each source
    if ean:
        row["ean_key"] = ean
        row[f"price_{source.replace('.com', '')}"] = price
        row[f"url_{source.replace('.com', '')}"] = row.get("url", "")
        row[f"available_{source.replace('.com', '')}"] = True
    
    return row
```

### Step 3: Final Aggregation (Group by EAN)

For the final matching table, you'll need to aggregate by EAN. This is typically done in a separate pipeline or using Spark SQL:

```yaml
# Pipeline: Final product matching table with aggregated prices
pipeline:
  - stage: load_csv
    args:
      - { path: "${OUTPUT_PATH_PRICE_COMPARISON_TABLE}", header: "true", inferSchema: "true" }
  
  # Use aggregation to group by EAN and collect prices from all sources
  - stage: aggregation_group_by_key
    args:
      - key_field: "ean_key"
        aggregations:
          - field: "price_amazon"
            type: "first"
            as: "price_amazon"
          - field: "price_ebay"
            type: "first"
            as: "price_ebay"
          - field: "price_walmart"
            type: "first"
            as: "price_walmart"
          - field: "price_target"
            type: "first"
            as: "price_target"
          - field: "price_bestbuy"
            type: "first"
            as: "price_bestbuy"
          - field: "product_name"
            type: "first"
            as: "product_name"
  
  # Calculate best price and best source
  - stage: python_row_transform:calculate_best_price
    args: []
  
  - stage: save_csv
    args: [ "${OUTPUT_PATH_FINAL_MATCHING_TABLE}", "overwrite" ]
```

```python
# python_extensions:
#   stages:
#     calculate_best_price:
#       type: row_transform
#       function: |
def calculate_best_price(row):
    """Calculate best price and source."""
    prices = {}
    sources = ["amazon", "ebay", "walmart", "target", "bestbuy"]
    
    for source in sources:
        price_key = f"price_{source}"
        price = row.get(price_key)
        if price and price > 0:
            prices[source] = price
    
    if prices:
        best_source = min(prices, key=prices.get)
        best_price = prices[best_source]
        
        row["best_price"] = best_price
        row["best_source"] = best_source
        row["price_difference_pct"] = ((max(prices.values()) - best_price) / best_price * 100) if len(prices) > 1 else 0
        row["sources_count"] = len(prices)
    
    return row
```

### Example Output: Product Matching Table

The final matching table will look like:

| ean | product_name | price_amazon | price_ebay | price_walmart | price_target | price_bestbuy | best_price | best_source | price_difference_pct | sources_count |
|-----|--------------|--------------|------------|---------------|--------------|---------------|-------------|-------------|----------------------|---------------|
| 0194253817003 | Apple iPhone 15 Pro Max 256GB | 1299.99 | 1249.99 | 1299.00 | 1299.99 | 1295.00 | 1249.99 | ebay | 4.0 | 5 |
| 0194253817004 | Samsung Galaxy S24 Ultra 512GB | 1199.99 | 1195.00 | 1199.00 | 1199.99 | 1198.00 | 1195.00 | ebay | 0.4 | 5 |
| 0194253817005 | Sony WH-1000XM5 Headphones | 399.99 | 389.99 | 399.00 | 399.99 | 395.00 | 389.99 | ebay | 2.5 | 5 |

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

