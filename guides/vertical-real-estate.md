---
title: Real Estate Arbitrage & Property Clustering
version: 1.0.0
description: "Complete guide for aggregating property listings from multiple sources, clustering similar properties, and detecting arbitrage opportunities using external statistical sources"
---

# Real Estate Arbitrage & Property Clustering

This guide demonstrates how to build **production-ready real estate arbitrage pipelines** that aggregate property listings from multiple sources, cluster similar properties, and detect undervalued opportunities by comparing prices against external statistical sources.

## Business Use Case

**Goal**: Build a unified property database by aggregating listings from multiple real estate sites, cluster similar properties to identify the same property across sources, and detect arbitrage opportunities when prices deviate significantly from market statistics.

**Key Challenges**:
- **Same property, different listings**: The same property can appear on multiple sites with different prices, descriptions, and photos
- **Property matching**: No universal identifier (like EAN for products), must use clustering based on address, features, and location
- **Market valuation**: Need external statistical sources to determine fair market value
- **Price deviation detection**: Identify properties priced significantly below market average

## Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Site A      │     │ Site B      │     │ Site C      │     │ Site D      │
│ (Crawl)     │     │ (Crawl)     │     │ (API)       │     │ (Crawl)     │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Union &   │
                    │  Normalize  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Geocode    │
                    │  Addresses  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Enrich     │
                    │ (Stats API) │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Cluster    │
                    │ Properties  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Detect     │
                    │ Arbitrage   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Save to    │
                    │   Storage   │
                    └─────────────┘
```

## Canonical Property Schema

A standardized schema is crucial for effective property matching and clustering:

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `property_id` | String | Unique property identifier (generated) | "prop_abc123" |
| `address` | String | Full address | "123 Main St, New York, NY 10001" |
| `address_normalized` | String | Normalized address for matching | "123 main street new york ny 10001" |
| `latitude` | Double | GPS latitude | 40.7128 |
| `longitude` | Double | GPS longitude | -74.0060 |
| `city` | String | City name | "New York" |
| `state` | String | State/Province | "NY" |
| `zip_code` | String | Postal code | "10001" |
| `price` | Double | Listing price | 500000.00 |
| `price_per_sqm` | Double | Price per square meter | 5000.00 |
| `area_sqm` | Double | Property area in square meters | 100.0 |
| `bedrooms` | Integer | Number of bedrooms | 3 |
| `bathrooms` | Double | Number of bathrooms | 2.5 |
| `property_type` | String | Type (apartment, house, etc.) | "apartment" |
| `source` | String | Source website | "zillow.com" |
| `url` | String | Listing URL | "https://www.zillow.com/..." |
| `listing_date` | Timestamp | When listing was posted | "2025-01-01T10:00:00Z" |
| `last_updated` | Timestamp | Last time data was extracted | "2025-01-15T10:30:00Z" |

## Concrete Example: Real Estate Arbitrage Detection

This example demonstrates a **complete production pipeline** that aggregates property listings from 5 major real estate sites, clusters similar properties, and detects arbitrage opportunities using external statistical sources.

### Real Estate Sites

1. **Zillow** - Direct crawl
2. **Realtor.com** - Direct crawl
3. **Trulia** - Direct crawl
4. **Redfin** - API-based (CSV input)
5. **Apartments.com** - Direct crawl

### Complete Pipeline: Multi-Source Aggregation with Clustering

```yaml
# Complete example: Real estate arbitrage detection with clustering
fetch:
  url: "https://www.zillow.com/homes/for_sale/"  # Starting URL for Zillow

pipeline:
  # ============================================
  # Site 1: Zillow (Direct crawl)
  # ============================================
  - stage: explore
    args: [ "a.pagination-next", 10 ]  # Navigate through search pages
  - stage: join
    args: [ "a.property-link", "LeftOuter" ]  # Click on property listings
  - stage: extract
    args:
      - { selector: "h1.property-title", method: "text", as: "title" }
      - { selector: "span.address", method: "text", as: "address" }
      - { selector: "span.price", method: "text", as: "price_raw" }
      - { selector: "span.sqft", method: "text", as: "area_sqft_raw" }
      - { selector: "span.bedrooms", method: "text", as: "bedrooms_raw" }
      - { selector: "span.bathrooms", method: "text", as: "bathrooms_raw" }
      - { selector: "span.property-type", method: "text", as: "property_type" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
      - { selector: "span.listing-date", method: "text", as: "listing_date" }
  - stage: python_row_transform:normalize_zillow
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - source: "zillow.com"
  - stage: cache
    args: []
  - stage: store
    args: [ "zillow_listings" ]

  # ============================================
  # Site 2: Realtor.com (Direct crawl)
  # ============================================
  - stage: reset
    args: []
  - stage: visit
    args: [ "https://www.realtor.com/realestateandhomes-search" ]
  - stage: explore
    args: [ "a.pagination-next", 10 ]
  - stage: join
    args: [ "a.property-card-link", "LeftOuter" ]
  - stage: extract
    args:
      - { selector: "h1.property-address", method: "text", as: "address" }
      - { selector: "span.price", method: "text", as: "price_raw" }
      - { selector: "span.sqft", method: "text", as: "area_sqft_raw" }
      - { selector: "span.beds", method: "text", as: "bedrooms_raw" }
      - { selector: "span.baths", method: "text", as: "bathrooms_raw" }
      - { selector: "span.property-type", method: "text", as: "property_type" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
  - stage: python_row_transform:normalize_realtor
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - source: "realtor.com"
  - stage: cache
    args: []
  - stage: store
    args: [ "realtor_listings" ]

  # ============================================
  # Site 3: Trulia (Direct crawl)
  # ============================================
  - stage: reset
    args: []
  - stage: visit
    args: [ "https://www.trulia.com/for_sale/" ]
  - stage: explore
    args: [ "a.pagination-next", 10 ]
  - stage: join
    args: [ "a.property-link", "LeftOuter" ]
  - stage: extract
    args:
      - { selector: "h1.address", method: "text", as: "address" }
      - { selector: "span.price", method: "text", as: "price_raw" }
      - { selector: "span.sqft", method: "text", as: "area_sqft_raw" }
      - { selector: "span.beds", method: "text", as: "bedrooms_raw" }
      - { selector: "span.baths", method: "text", as: "bathrooms_raw" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
  - stage: python_row_transform:normalize_trulia
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - source: "trulia.com"
  - stage: cache
    args: []
  - stage: store
    args: [ "trulia_listings" ]

  # ============================================
  # Site 4: Redfin (API-based - CSV input)
  # ============================================
  - stage: reset
    args: []
  - stage: load_csv
    args:
      - { path: "${REDFIN_API_RESPONSE_PATH}", header: "true", inferSchema: "true" }
  - stage: python_row_transform:normalize_redfin
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - source: "redfin.com"
  - stage: cache
    args: []
  - stage: store
    args: [ "redfin_listings" ]

  # ============================================
  # Site 5: Apartments.com (Direct crawl)
  # ============================================
  - stage: reset
    args: []
  - stage: visit
    args: [ "https://www.apartments.com/apartments/" ]
  - stage: explore
    args: [ "a.pagination-next", 10 ]
  - stage: join
    args: [ "a.property-link", "LeftOuter" ]
  - stage: extract
    args:
      - { selector: "h1.address", method: "text", as: "address" }
      - { selector: "span.rent", method: "text", as: "price_raw" }
      - { selector: "span.sqft", method: "text", as: "area_sqft_raw" }
      - { selector: "span.beds", method: "text", as: "bedrooms_raw" }
      - { selector: "span.baths", method: "text", as: "bathrooms_raw" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
  - stage: python_row_transform:normalize_apartments
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - source: "apartments.com"
  - stage: cache
    args: []
  - stage: store
    args: [ "apartments_listings" ]

  # ============================================
  # Merge: Union all sources
  # ============================================
  - stage: reset
    args: []
  - stage: union_with
    args: [ "zillow_listings", "realtor_listings", "trulia_listings", "redfin_listings", "apartments_listings" ]

  # ============================================
  # Normalize Addresses and Geocode
  # ============================================
  - stage: python_row_transform:normalize_address
    args: []
  - stage: python_row_transform:geocode_address
    args: []  # Uses external geocoding API

  # ============================================
  # Calculate Price per Square Meter
  # ============================================
  - stage: python_row_transform:calculate_price_per_sqm
    args: []

  # ============================================
  # Enrich with External Statistical Sources
  # ============================================
  - stage: python_row_transform:enrich_with_market_stats
    args: []  # Fetches average prices per zip code, neighborhood stats, etc.

  # ============================================
  # Cluster Properties (Identify Same Property)
  # ============================================
  - stage: propertyCluster
    args:
      - algorithm: "kmeans"
        k: 50
        features: ["latitude", "longitude", "price_per_sqm", "area_sqm", "bedrooms", "bathrooms"]
        epsilon: 0.5
        minPoints: 2

  # ============================================
  # Detect Arbitrage Opportunities
  # Compare prices within clusters and against market statistics
  # ============================================
  - stage: python_row_transform:detect_arbitrage_opportunities
    args:
      - price_deviation_threshold: 0.15  # 15% below market average
      - cluster_price_variance_threshold: 0.20  # 20% variance within cluster

  # ============================================
  # Save Results
  # ============================================
  - stage: save_csv
    args: [ "${OUTPUT_PATH_ARBITRAGE_OPPORTUNITIES}", "overwrite" ]
```

### Python Extensions for Property Normalization

```python
# python_extensions:
#   stages:
#     normalize_zillow:
#       type: row_transform
#       function: |
def normalize_zillow(row):
    """Normalize Zillow property data."""
    # Parse price
    price_raw = row.get("price_raw", "").replace("$", "").replace(",", "").strip()
    try:
        row["price"] = float(price_raw)
    except:
        row["price"] = None
    
    # Parse area (sqft to sqm)
    area_sqft_raw = row.get("area_sqft_raw", "").replace(",", "").replace("sqft", "").strip()
    try:
        area_sqft = float(area_sqft_raw)
        row["area_sqm"] = area_sqft * 0.092903  # Convert sqft to sqm
    except:
        row["area_sqm"] = None
    
    # Parse bedrooms/bathrooms
    bedrooms_raw = row.get("bedrooms_raw", "").replace("bed", "").replace("beds", "").strip()
    try:
        row["bedrooms"] = int(bedrooms_raw)
    except:
        row["bedrooms"] = None
    
    bathrooms_raw = row.get("bathrooms_raw", "").replace("bath", "").replace("baths", "").strip()
    try:
        row["bathrooms"] = float(bathrooms_raw)
    except:
        row["bathrooms"] = None
    
    return row

#     normalize_address:
#       type: row_transform
#       function: |
def normalize_address(row):
    """Normalize address for matching."""
    import re
    
    address = row.get("address", "").strip()
    
    # Remove common suffixes and normalize
    address = re.sub(r'\s+(St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Dr|Drive|Ln|Lane)\s*$', '', address, flags=re.IGNORECASE)
    address = re.sub(r'\s+', ' ', address).strip()
    address = address.lower()
    
    # Extract components
    parts = address.split(',')
    if len(parts) >= 2:
        row["city"] = parts[-2].strip() if len(parts) >= 2 else ""
        state_zip = parts[-1].strip().split()
        if len(state_zip) >= 2:
            row["state"] = state_zip[0].upper()
            row["zip_code"] = state_zip[1] if len(state_zip) > 1 else ""
    
    row["address_normalized"] = address
    
    return row

#     geocode_address:
#       type: row_transform
#       function: |
def geocode_address(row):
    """Geocode address to get latitude/longitude."""
    import requests
    
    address = row.get("address", "")
    if not address:
        return row
    
    # Use external geocoding API (e.g., Google Maps, OpenStreetMap)
    # In production, use proper API with rate limiting
    try:
        # Example using Nominatim (OpenStreetMap) - free but rate-limited
        url = f"https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1
        }
        headers = {"User-Agent": "WebRobot-ETL/1.0"}
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data:
                row["latitude"] = float(data[0]["lat"])
                row["longitude"] = float(data[0]["lon"])
    except Exception as e:
        # Fallback: set to None if geocoding fails
        row["latitude"] = None
        row["longitude"] = None
    
    return row

#     calculate_price_per_sqm:
#       type: row_transform
#       function: |
def calculate_price_per_sqm(row):
    """Calculate price per square meter."""
    price = row.get("price", 0)
    area_sqm = row.get("area_sqm", 0)
    
    if price and area_sqm and area_sqm > 0:
        row["price_per_sqm"] = price / area_sqm
    else:
        row["price_per_sqm"] = None
    
    return row

#     enrich_with_market_stats:
#       type: row_transform
#       function: |
def enrich_with_market_stats(row):
    """Enrich property with external market statistics."""
    import requests
    
    zip_code = row.get("zip_code", "")
    city = row.get("city", "")
    
    if not zip_code:
        return row
    
    # Fetch market statistics from external API
    # Example: Zillow API, Redfin API, or custom statistical service
    try:
        # Example API call (replace with actual API)
        url = f"https://api.marketstats.example.com/stats"
        params = {
            "zip_code": zip_code,
            "city": city
        }
        headers = {"Authorization": "Bearer ${MARKET_STATS_API_KEY}"}
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            stats = response.json()
            row["market_avg_price_per_sqm"] = stats.get("avg_price_per_sqm", None)
            row["market_median_price"] = stats.get("median_price", None)
            row["market_price_per_sqm_p25"] = stats.get("price_per_sqm_p25", None)  # 25th percentile
            row["market_price_per_sqm_p75"] = stats.get("price_per_sqm_p75", None)  # 75th percentile
            row["market_listings_count"] = stats.get("listings_count", None)
    except Exception as e:
        # If API fails, set to None
        row["market_avg_price_per_sqm"] = None
        row["market_median_price"] = None
    
    return row

#     detect_arbitrage_opportunities:
#       type: row_transform
#       function: |
def detect_arbitrage_opportunities(row, price_deviation_threshold=0.15, cluster_price_variance_threshold=0.20):
    """Detect arbitrage opportunities by comparing prices within clusters and against market stats."""
    price_per_sqm = row.get("price_per_sqm", 0)
    market_avg_price_per_sqm = row.get("market_avg_price_per_sqm", None)
    cluster_id = row.get("cluster_id", None)
    
    opportunities = []
    
    # 1. Compare against market average
    if market_avg_price_per_sqm and price_per_sqm:
        deviation = (market_avg_price_per_sqm - price_per_sqm) / market_avg_price_per_sqm
        if deviation >= price_deviation_threshold:
            opportunities.append("below_market_avg")
            row["price_deviation_from_market"] = deviation
            row["potential_savings_pct"] = deviation * 100
    
    # 2. Compare against market percentiles
    market_p25 = row.get("market_price_per_sqm_p25", None)
    market_p75 = row.get("market_price_per_sqm_p75", None)
    
    if market_p25 and price_per_sqm and price_per_sqm < market_p25:
        opportunities.append("below_p25")
        row["below_25th_percentile"] = True
    
    if market_p75 and price_per_sqm and price_per_sqm > market_p75:
        opportunities.append("above_p75")
        row["above_75th_percentile"] = True
    
    # 3. Cluster-based detection (same property, different prices)
    # This would require aggregating by cluster_id first
    # For now, mark for later cluster analysis
    if cluster_id:
        row["cluster_analysis_needed"] = True
    
    row["arbitrage_opportunities"] = ",".join(opportunities) if opportunities else None
    row["is_arbitrage_opportunity"] = len(opportunities) > 0
    
    return row
```

## Property Clustering: Identifying the Same Property

### Clustering Strategy

Properties are clustered using **ML-based clustering** (`propertyCluster` stage) based on:

1. **Location Features**: `latitude`, `longitude` (GPS coordinates)
2. **Price Features**: `price_per_sqm` (normalized price)
3. **Size Features**: `area_sqm` (property size)
4. **Feature Features**: `bedrooms`, `bathrooms` (property characteristics)

### Clustering Algorithm

The `propertyCluster` stage supports:
- **K-Means**: Groups properties into k clusters based on feature similarity
- **DBSCAN**: Density-based clustering (identifies outliers)
- **Gaussian Mixture Model**: Probabilistic clustering

### Post-Clustering Analysis

After clustering, analyze clusters to:
1. **Identify same property**: Properties in the same cluster with similar address = likely the same property
2. **Price variance within cluster**: High variance indicates price arbitrage opportunity
3. **Compare cluster average to market**: Cluster average significantly below market = opportunity

```sql
-- Downstream post-clustering analysis (recommended: Trino/Spark SQL)
-- Build cluster-level stats and arbitrage signals from the row-level clustered dataset.
SELECT
  cluster_id,
  avg(price_per_sqm) AS cluster_avg_price_per_sqm,
  stddev_pop(price_per_sqm) AS cluster_price_stddev,
  min(price_per_sqm) AS cluster_min_price_per_sqm,
  max(price_per_sqm) AS cluster_max_price_per_sqm,
  count(*) AS listings_in_cluster
FROM clustered_properties
GROUP BY 1;
```

Use the cluster-level stats above to flag opportunities (e.g., high intra-cluster variance, low percentile vs market stats) and then join back to row-level listings for actionable results.

## External Statistical Sources Integration

### Market Statistics APIs

Integrate with external statistical sources to get:
- **Average prices per zip code**: Compare listing price to neighborhood average
- **Price percentiles**: Identify if property is in bottom 25% (undervalued)
- **Historical price trends**: Track price changes over time
- **Comparable sales**: Recent sales of similar properties in the area

### Example Statistical Sources

1. **Zillow API**: Zestimate, market trends, comparable sales
2. **Redfin API**: Market statistics, price history
3. **Census Bureau API**: Demographics, income data
4. **Custom Statistical Service**: Aggregated data from multiple sources

## Example Output: Arbitrage Opportunities Table

The final output will contain properties flagged as arbitrage opportunities:

| property_id | address | price | price_per_sqm | market_avg_price_per_sqm | price_deviation_from_market | cluster_id | cluster_arbitrage_exists | is_arbitrage_opportunity | sources |
|-------------|---------|-------|---------------|--------------------------|----------------------------|------------|-------------------------|-------------------------|---------|
| prop_123 | 123 Main St, NY | 450000 | 4500 | 5500 | 0.18 | cluster_5 | True | True | zillow,realtor |
| prop_456 | 456 Oak Ave, NY | 380000 | 3800 | 4800 | 0.21 | cluster_12 | False | True | trulia,redfin |
| prop_789 | 789 Elm St, NY | 520000 | 5200 | 5100 | -0.02 | cluster_8 | True | True | zillow,apartments |

## API Endpoints for Real Estate Arbitrage

After processing, query the arbitrage opportunities:

#### Get Arbitrage Opportunities

```http
GET /api/webrobot/api/datasets/{datasetId}/query?sqlQuery=SELECT * FROM arbitrage_opportunities WHERE is_arbitrage_opportunity = true AND price_deviation_from_market > 0.15 ORDER BY price_deviation_from_market DESC
```

#### Get Properties in Same Cluster

```http
GET /api/webrobot/api/datasets/{datasetId}/query?sqlQuery=SELECT * FROM clustered_properties WHERE cluster_id = 'cluster_5' ORDER BY price
```

