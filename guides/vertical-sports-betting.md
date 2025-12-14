---
title: Sports Betting & Odds Aggregation
version: 1.0.0
description: "Complete guide for aggregating betting odds from multiple bookmakers, detecting arbitrage opportunities, and managing betting risk"
---

# Sports Betting & Odds Aggregation

This guide demonstrates how to build **production-ready sports betting pipelines** that aggregate odds from multiple bookmakers, detect arbitrage opportunities, and track odds movements over time.

## Business Use Case

**Goal**: Build a unified odds comparison system by aggregating betting odds from multiple bookmakers, enabling:

- **Odds comparison**: Compare odds for the same event/market across different bookmakers
- **Arbitrage detection**: Identify opportunities where the combined odds guarantee profit
- **Odds tracking**: Monitor odds movements and line movements over time
- **Risk management**: Calculate optimal bet sizing and manage exposure

## Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Bookmaker A │     │ Bookmaker B │     │ Bookmaker C │     │ Bookmaker D │
│  (Crawl)    │     │  (API)      │     │  (Crawl)    │     │  (API)      │
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
                    │  Match by   │
                    │ Event/Market│
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Calculate  │
                    │  Arbitrage  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Save to    │
                    │   Storage   │
                    └─────────────┘
```

## Canonical Odds Schema

A standardized schema is crucial for effective odds comparison:

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `event_id` | String | Unique event identifier (e.g., match_id) | "match_20250101_team1_team2" |
| `event_name` | String | Human-readable event name | "Manchester United vs Liverpool" |
| `event_date` | Timestamp | Event start date/time | "2025-01-15T15:00:00Z" |
| `sport` | String | Sport type | "football", "basketball", "tennis" |
| `market_type` | String | Betting market type | "match_winner", "over_under", "handicap" |
| `selection` | String | Betting selection/outcome | "home_win", "away_win", "draw", "over_2.5" |
| `odds_decimal` | Double | Decimal odds (e.g., 2.50) | 2.50 |
| `odds_fractional` | String | Fractional odds (e.g., "3/2") | "3/2" |
| `odds_american` | String | American odds (e.g., "+150") | "+150" |
| `bookmaker` | String | Bookmaker name | "bet365", "pinnacle", "betfair" |
| `url` | String | URL of the betting page | "https://www.bet365.com/event/12345" |
| `last_updated` | Timestamp | Last time odds were extracted | "2025-01-01T10:30:00Z" |

## Concrete Example: Aggregating Odds from 5 Bookmakers

### Pipeline Pattern: Multi-Source Union with Event Matching

This example shows how to aggregate odds from 5 different bookmakers for the same football match:

```yaml
# Complete example: Multi-bookmaker odds aggregation
fetch:
  url: "https://www.bet365.com/football"  # Starting URL for Bookmaker A

pipeline:
  # ============================================
  # Bookmaker A: bet365 (Direct crawl)
  # ============================================
  - stage: explore
    args: [ "a.match-link", 10 ]  # Navigate to match pages
  - stage: join
    args: [ "div.market-container", "LeftOuter" ]
  - stage: extract
    args:
      - { selector: "h1.match-title", method: "text", as: "event_name" }
      - { selector: "span.match-date", method: "attr:data-timestamp", as: "event_date" }
      - { selector: "div.market-type", method: "text", as: "market_type" }
      - { selector: "span.selection-name", method: "text", as: "selection" }
      - { selector: "span.odds-decimal", method: "text", as: "odds_raw" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
  - stage: python_row_transform:normalize_bet365
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - bookmaker: "bet365"
        sport: "football"
  - stage: cache
    args: []
  - stage: store
    args: [ "bookmaker_a" ]

  # ============================================
  # Bookmaker B: Pinnacle (API-based)
  # ============================================
  - stage: reset
    args: []
  - stage: load_csv
    args:
      - { path: "${PINNACLE_API_RESPONSE_PATH}", header: "true", inferSchema: "true" }
  - stage: python_row_transform:normalize_pinnacle
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - bookmaker: "pinnacle"
        sport: "football"
  - stage: cache
    args: []
  - stage: store
    args: [ "bookmaker_b" ]

  # ============================================
  # Bookmaker C: Betfair (Crawl)
  # ============================================
  - stage: reset
    args: []
  - stage: visit
    args: [ "https://www.betfair.com/sport/football" ]
  - stage: explore
    args: [ "a.event-link", 10 ]
  - stage: join
    args: [ "div.market-row", "LeftOuter" ]
  - stage: extract
    args:
      - { selector: "span.event-name", method: "text", as: "event_name" }
      - { selector: "span.event-time", method: "attr:data-time", as: "event_date" }
      - { selector: "span.market-name", method: "text", as: "market_type" }
      - { selector: "span.selection", method: "text", as: "selection" }
      - { selector: "span.odds", method: "text", as: "odds_raw" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
  - stage: python_row_transform:normalize_betfair
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - bookmaker: "betfair"
        sport: "football"
  - stage: cache
    args: []
  - stage: store
    args: [ "bookmaker_c" ]

  # ============================================
  # Bookmaker D: William Hill (Crawl)
  # ============================================
  - stage: reset
    args: []
  - stage: visit
    args: [ "https://sports.williamhill.com/betting/en-gb/football" ]
  - stage: explore
    args: [ "a.event", 10 ]
  - stage: join
    args: [ "div.bet-market", "LeftOuter" ]
  - stage: extract
    args:
      - { selector: "h2.event-title", method: "text", as: "event_name" }
      - { selector: "time.event-date", method: "attr:datetime", as: "event_date" }
      - { selector: "span.market", method: "text", as: "market_type" }
      - { selector: "button.selection", method: "text", as: "selection" }
      - { selector: "span.price", method: "text", as: "odds_raw" }
      - { selector: "link[rel=canonical]", method: "attr:href", as: "url" }
  - stage: python_row_transform:normalize_williamhill
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - bookmaker: "williamhill"
        sport: "football"
  - stage: cache
    args: []
  - stage: store
    args: [ "bookmaker_d" ]

  # ============================================
  # Bookmaker E: Unibet (API-based)
  # ============================================
  - stage: reset
    args: []
  - stage: load_csv
    args:
      - { path: "${UNIBET_API_RESPONSE_PATH}", header: "true", inferSchema: "true" }
  - stage: python_row_transform:normalize_unibet
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - bookmaker: "unibet"
        sport: "football"
  - stage: cache
    args: []
  - stage: store
    args: [ "bookmaker_e" ]

  # ============================================
  # Merge: Union all bookmakers
  # ============================================
  - stage: reset
    args: []
  - stage: union_with
    args: [ "bookmaker_a", "bookmaker_b", "bookmaker_c", "bookmaker_d", "bookmaker_e" ]

  # ============================================
  # Normalize event matching keys
  # ============================================
  - stage: python_row_transform:generate_event_id
    args: []  # Creates event_id from event_name + event_date

  # ============================================
  # Save unified odds dataset
  # ============================================
  - stage: save_csv
    args: [ "${OUTPUT_PATH_UNIFIED_ODDS}", "overwrite" ]
```

### Python Extensions for Odds Normalization

```python
# python_extensions:
#   stages:
#     normalize_bet365:
#       type: row_transform
#       function: |
def normalize_bet365(row):
    """Normalize bet365 odds format to decimal."""
    odds_raw = row.get("odds_raw", "")
    if odds_raw:
        # bet365 format: "2.50" or "3/2" -> convert to decimal
        try:
            if "/" in odds_raw:
                # Fractional odds: "3/2" -> 2.50
                parts = odds_raw.split("/")
                decimal = (float(parts[0]) / float(parts[1])) + 1
                row["odds_decimal"] = round(decimal, 2)
            else:
                row["odds_decimal"] = float(odds_raw)
        except:
            row["odds_decimal"] = None
    return row

#     normalize_pinnacle:
#       type: row_transform
#       function: |
def normalize_pinnacle(row):
    """Normalize Pinnacle API response to canonical format."""
    # Pinnacle API returns decimal odds directly
    row["odds_decimal"] = float(row.get("odds", 0))
    row["event_name"] = row.get("eventName", "")
    row["selection"] = row.get("selectionName", "")
    return row

#     generate_event_id:
#       type: row_transform
#       function: |
def generate_event_id(row):
    """Generate stable event_id for matching across bookmakers."""
    import hashlib
    event_name = row.get("event_name", "").lower().strip()
    event_date = row.get("event_date", "")
    # Normalize event name (remove special chars, standardize team names)
    normalized = f"{event_name}_{event_date}"
    event_id = hashlib.md5(normalized.encode()).hexdigest()[:16]
    row["event_id"] = f"event_{event_id}"
    return row
```

## Event Matching Logic: Recognizing the Same Sports Event Across Bookmakers

**Critical Challenge**: The same sports event can appear with **different names and formats** across different bookmakers. For example:
- "Manchester United vs Liverpool" vs "Man Utd v Liverpool" vs "MUFC vs LFC"
- "Arsenal vs Chelsea FC" vs "Arsenal vs Chelsea" vs "Arsenal v Chelsea"
- Date formats: "2025-01-15 15:00" vs "15/01/2025 3:00 PM" vs "Jan 15, 2025"

The surebet finder **must consult aggregated odds by event** to detect arbitrage opportunities.

### Event Matching Strategy

1. **Event Normalization**:
   - Standardize team names (abbreviations, full names, aliases)
   - Normalize date/time formats
   - Remove special characters and standardize separators
   - Handle league/competition variations

2. **Event ID Generation**:
   - Create stable `event_id` from normalized event name + date
   - Use hashing for consistent matching across bookmakers

3. **Aggregation by Event**: All odds comparisons must be **aggregated by event_id** before surebet detection.

### Event Name Normalization

```python
# python_extensions:
#   stages:
#     normalize_event_name:
#       type: row_transform
#       function: |
def normalize_event_name(row):
    """Normalize event name for matching across bookmakers."""
    import re
    from datetime import datetime
    
    event_name = row.get("event_name", "").strip()
    event_date = row.get("event_date", "")
    
    # Common team name mappings (expand as needed)
    team_mappings = {
        "manchester united": ["man utd", "manchester utd", "mufc", "man united"],
        "liverpool": ["liverpool fc", "lfc"],
        "arsenal": ["arsenal fc"],
        "chelsea": ["chelsea fc", "cfc"],
        "tottenham": ["tottenham hotspur", "spurs", "tottenham fc"],
        "manchester city": ["man city", "mcfc", "manchester city fc"],
        # Add more mappings as needed
    }
    
    # Normalize event name
    event_name_lower = event_name.lower()
    
    # Replace common separators
    event_name_lower = re.sub(r'\s+vs\.?\s+', ' vs ', event_name_lower)
    event_name_lower = re.sub(r'\s+v\.?\s+', ' vs ', event_name_lower)
    event_name_lower = re.sub(r'\s+-\s+', ' vs ', event_name_lower)
    
    # Standardize team names
    for standard_name, variations in team_mappings.items():
        for variation in variations:
            event_name_lower = event_name_lower.replace(variation, standard_name)
    
    # Remove common prefixes/suffixes
    event_name_lower = re.sub(r'^(live|upcoming|today|tomorrow)\s+', '', event_name_lower)
    event_name_lower = re.sub(r'\s+(live|upcoming|today|tomorrow)$', '', event_name_lower)
    
    # Normalize whitespace
    event_name_lower = re.sub(r'\s+', ' ', event_name_lower).strip()
    
    row["event_name_normalized"] = event_name_lower
    
    # Normalize event date
    if event_date:
        try:
            # Try to parse various date formats
            date_formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
                "%d/%m/%Y %H:%M",
                "%m/%d/%Y %H:%M",
                "%d-%m-%Y %H:%M",
                "%Y-%m-%d %H:%M",
            ]
            
            parsed_date = None
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(event_date, fmt)
                    break
                except:
                    continue
            
            if parsed_date:
                # Standardize to ISO format
                row["event_date_normalized"] = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                row["event_date_normalized"] = event_date
        except:
            row["event_date_normalized"] = event_date
    else:
        row["event_date_normalized"] = ""
    
    return row

#     generate_event_id:
#       type: row_transform
#       function: |
def generate_event_id(row):
    """Generate stable event_id for matching across bookmakers."""
    import hashlib
    
    event_name = row.get("event_name_normalized", "").lower().strip()
    event_date = row.get("event_date_normalized", "")
    sport = row.get("sport", "football").lower()
    
    # Create normalized key
    normalized_key = f"{sport}_{event_name}_{event_date}"
    
    # Remove special characters for consistent hashing
    normalized_key = normalized_key.replace(" ", "_").replace("-", "_")
    normalized_key = "".join(c for c in normalized_key if c.isalnum() or c == "_")
    
    # Generate hash-based event_id
    event_id_hash = hashlib.md5(normalized_key.encode()).hexdigest()[:16]
    row["event_id"] = f"event_{event_id_hash}"
    
    return row
```

### Aggregation by Event ID

Before surebet detection, **aggregate all odds by event_id**:

```yaml
# Pipeline: Aggregate odds by event for surebet detection
pipeline:
  - stage: load_csv
    args:
      - { path: "${OUTPUT_PATH_UNIFIED_ODDS}", header: "true", inferSchema: "true" }
  
  # Normalize event names and dates
  - stage: python_row_transform:normalize_event_name
    args: []
  
  # Generate stable event_id
  - stage: python_row_transform:generate_event_id
    args: []
  
  # Create matching key (event_id + market_type + selection)
  - stage: python_row_transform:create_matching_key
    args: []
  
  # Aggregate by event_id + market_type + selection
  # Collect odds from all bookmakers for the same event/market/selection
  - stage: aggregation_group_by_key
    args:
      - key_field: "matching_key"
        aggregations:
          - field: "odds_decimal"
            type: "collect_list"
            as: "odds_by_bookmaker"
          - field: "bookmaker"
            type: "collect_list"
            as: "bookmakers"
          - field: "url"
            type: "collect_list"
            as: "urls"
          - field: "event_name_normalized"
            type: "first"
            as: "event_name_canonical"
          - field: "market_type"
            type: "first"
            as: "market_type"
          - field: "selection"
            type: "first"
            as: "selection"
          - field: "event_id"
            type: "first"
            as: "event_id"
  
  # Create odds comparison columns (pivot-like structure)
  - stage: python_row_transform:create_odds_comparison_by_event
    args: []
  
  # Detect surebet opportunities
  - stage: python_row_transform:detect_surebet_by_event
    args:
      - min_profit_margin: 0.02  # Minimum 2% profit margin
  
  - stage: save_csv
    args: [ "${OUTPUT_PATH_SUREBET_BY_EVENT}", "overwrite" ]
```

```python
# python_extensions:
#   stages:
#     create_odds_comparison_by_event:
#       type: row_transform
#       function: |
def create_odds_comparison_by_event(row):
    """Create odds comparison columns grouped by event."""
    odds_by_bookmaker = row.get("odds_by_bookmaker", [])
    bookmakers = row.get("bookmakers", [])
    urls = row.get("urls", [])
    
    # Create columns for each bookmaker
    bookmaker_odds_map = {}
    bookmaker_url_map = {}
    
    for i, bookmaker in enumerate(bookmakers):
        bookmaker_clean = bookmaker.replace(".com", "").replace(".", "_").lower()
        if i < len(odds_by_bookmaker) and odds_by_bookmaker[i]:
            bookmaker_odds_map[f"odds_{bookmaker_clean}"] = odds_by_bookmaker[i]
        if i < len(urls) and urls[i]:
            bookmaker_url_map[f"url_{bookmaker_clean}"] = urls[i]
    
    # Add odds columns
    for key, value in bookmaker_odds_map.items():
        row[key] = value
    
    # Add URL columns
    for key, value in bookmaker_url_map.items():
        row[key] = value
    
    row["bookmakers_count"] = len(bookmakers)
    
    return row

#     detect_surebet_by_event:
#       type: row_transform
#       function: |
def detect_surebet_by_event(row, min_profit_margin=0.02):
    """Detect surebet opportunities for an event/market by consulting aggregated odds."""
    # For match_winner market with 3 outcomes (home, draw, away)
    # We need to find all outcomes for the same event + market
    
    # Get all odds for this event/market from different bookmakers
    bookmakers = ["bet365", "pinnacle", "betfair", "williamhill", "unibet"]
    
    # Collect odds for each outcome
    odds_home = []
    odds_draw = []
    odds_away = []
    
    for bookmaker in bookmakers:
        odds_key = f"odds_{bookmaker}"
        odds = row.get(odds_key)
        if odds and odds > 0:
            # Determine which outcome this is based on selection
            selection = row.get("selection", "").lower()
            if "home" in selection or "1" in selection:
                odds_home.append(odds)
            elif "draw" in selection or "x" in selection or "tie" in selection:
                odds_draw.append(odds)
            elif "away" in selection or "2" in selection:
                odds_away.append(odds)
    
    # Find best odds for each outcome across all bookmakers
    best_home = min(odds_home) if odds_home else 999
    best_draw = min(odds_draw) if odds_draw else 999
    best_away = min(odds_away) if odds_away else 999
    
    # Calculate implied probability
    if best_home > 0 and best_draw > 0 and best_away > 0:
        implied_prob = (1/best_home) + (1/best_draw) + (1/best_away)
        
        # Surebet exists if implied_prob < 1.0
        if implied_prob < 1.0:
            profit_margin = (1.0 - implied_prob) * 100  # Percentage profit
            
            if profit_margin >= min_profit_margin * 100:
                row["surebet_exists"] = True
                row["surebet_profit_pct"] = profit_margin
                row["best_home_odds"] = best_home
                row["best_draw_odds"] = best_draw
                row["best_away_odds"] = best_away
                row["implied_probability"] = implied_prob
            else:
                row["surebet_exists"] = False
                row["surebet_profit_pct"] = 0.0
        else:
            row["surebet_exists"] = False
            row["surebet_profit_pct"] = 0.0
    
    return row
```

## Event Matching & Odds Comparison Table

After aggregating odds from all bookmakers **by event_id**, create a **comparison table** that shows odds for the same event/market across all bookmakers. The surebet finder **consults these aggregated odds by event** to detect arbitrage opportunities.

### Step 1: Generate Event Matching Table

```yaml
# Pipeline: Generate event matching table
pipeline:
  - stage: load_csv
    args:
      - { path: "${OUTPUT_PATH_UNIFIED_ODDS}", header: "true", inferSchema: "true" }
  
  # Group by event_id + market_type + selection to create matching table
  - stage: python_row_transform:create_matching_key
    args: []  # Creates key: event_id + market_type + selection
  
  # Save matching table
  - stage: save_csv
    args: [ "${OUTPUT_PATH_MATCHING_TABLE}", "overwrite" ]
```

### Step 2: Pivot Table for Odds Comparison

```python
# python_extensions:
#   stages:
#     create_matching_key:
#       type: row_transform
#       function: |
def create_matching_key(row):
    """Create a matching key for event + market + selection."""
    event_id = row.get("event_id", "")
    market_type = row.get("market_type", "").lower().replace(" ", "_")
    selection = row.get("selection", "").lower().replace(" ", "_")
    row["matching_key"] = f"{event_id}_{market_type}_{selection}"
    return row
```

### Example Output: Odds Comparison Table

The final matching table will look like:

| event_id | event_name | market_type | selection | bet365 | pinnacle | betfair | williamhill | unibet | best_odds | best_bookmaker |
|----------|------------|-------------|-----------|--------|----------|---------|-------------|--------|------------|----------------|
| event_123 | Man Utd vs Liverpool | match_winner | home_win | 2.10 | 2.15 | 2.12 | 2.08 | 2.13 | 2.15 | pinnacle |
| event_123 | Man Utd vs Liverpool | match_winner | away_win | 3.50 | 3.45 | 3.55 | 3.60 | 3.48 | 3.60 | williamhill |
| event_123 | Man Utd vs Liverpool | match_winner | draw | 3.20 | 3.25 | 3.18 | 3.22 | 3.24 | 3.25 | pinnacle |

## Concrete Example: Surebet Detection with Intelligent Navigation

This example demonstrates how to use **intelligent navigation** (`intelligent_explore`) and **intelligent table extraction** (`intelligent_flatSelect`) to extract odds from bookmaker sites with complex, non-trivial table structures.

### Challenge: Complex Table Structures

Many bookmaker sites use:
- **Dynamic tables** with JavaScript-rendered content
- **Nested structures** where odds are in different containers
- **Non-standard HTML** that doesn't follow simple CSS selector patterns
- **Multiple market types** on the same page (match winner, over/under, handicaps, etc.)

### Solution: Intelligent Extraction

Use `intelligent_explore` for navigation and `intelligent_flatSelect` for extracting odds from complex table structures:

```yaml
# Complete example: Surebet detection with intelligent extraction
fetch:
  url: "https://www.bet365.com/football"
  traces:
    - { action: "visit", params: { url: "https://www.bet365.com/football", cooldown: 1.0 } }
    - { action: "wait", params: { seconds: 2 } }  # Wait for dynamic content to load

pipeline:
  # ============================================
  # Step 1: Intelligent Navigation
  # Navigate through match/event pages using LLM to find links
  # ============================================
  - stage: intelligent_explore
    args: 
      - "links to football match pages or event listings"  # Segmentation prompt
      - 3  # Depth: navigate 3 levels deep

  # ============================================
  # Step 2: Intelligent Table Extraction
  # Extract odds from complex table structures using LLM
  # ============================================
  - stage: intelligent_flatSelect
    args:
      # Segmentation prompt: Find repeated elements (rows/cards) containing betting markets
      - "repeated betting market rows or cards, each containing a market type and multiple selection options with odds"
      # Extraction prompt: Extract structured data from each segment
      - "Extract: event_name (match/event title), event_date (date/time), market_type (e.g., match_winner, over_under, handicap), selection (e.g., home_win, away_win, draw, over_2.5, under_2.5), odds_decimal (decimal odds as number), odds_raw (original odds string)"
      # Optional prefix for extracted fields
      - "bet365_"  # Prefix for all extracted fields

  # ============================================
  # Step 3: Normalize and Enrich
  # ============================================
  - stage: python_row_transform:normalize_bet365_intelligent
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - bookmaker: "bet365"
        sport: "football"
        extraction_method: "intelligent"

  # ============================================
  # Step 4: Cache and Store
  # ============================================
  - stage: cache
    args: []
  - stage: store
    args: [ "bet365_offers" ]

  # ============================================
  # Repeat for other bookmakers...
  # ============================================
  # Bookmaker 2: Pinnacle (similar pattern)
  - stage: reset
    args: []
  - stage: visit
    args: [ "https://www.pinnacle.com/en/football" ]
  - stage: intelligent_explore
    args:
      - "links to football match pages"
      - 2
  - stage: intelligent_flatSelect
    args:
      - "betting market sections with odds for different selections"
      - "Extract: event_name, event_date, market_type, selection, odds_decimal, odds_raw"
      - "pinnacle_"
  - stage: python_row_transform:normalize_pinnacle_intelligent
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - bookmaker: "pinnacle"
        sport: "football"
        extraction_method: "intelligent"
  - stage: cache
    args: []
  - stage: store
    args: [ "pinnacle_offers" ]

  # Bookmaker 3: Betfair
  - stage: reset
    args: []
  - stage: visit
    args: [ "https://www.betfair.com/sport/football" ]
  - stage: intelligent_explore
    args:
      - "event or match links in the football section"
      - 2
  - stage: intelligent_flatSelect
    args:
      - "betting market rows or cards with selection buttons and odds"
      - "Extract: event_name, event_date, market_type, selection, odds_decimal, odds_raw"
      - "betfair_"
  - stage: python_row_transform:normalize_betfair_intelligent
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - bookmaker: "betfair"
        sport: "football"
        extraction_method: "intelligent"
  - stage: cache
    args: []
  - stage: store
    args: [ "betfair_offers" ]

  # Bookmaker 4: William Hill
  - stage: reset
    args: []
  - stage: visit
    args: [ "https://sports.williamhill.com/betting/en-gb/football" ]
  - stage: intelligent_explore
    args:
      - "football match or event links"
      - 2
  - stage: intelligent_flatSelect
    args:
      - "betting market containers with selection options and price buttons"
      - "Extract: event_name, event_date, market_type, selection, odds_decimal, odds_raw"
      - "williamhill_"
  - stage: python_row_transform:normalize_williamhill_intelligent
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - bookmaker: "williamhill"
        sport: "football"
        extraction_method: "intelligent"
  - stage: cache
    args: []
  - stage: store
    args: [ "williamhill_offers" ]

  # Bookmaker 5: Unibet
  - stage: reset
    args: []
  - stage: visit
    args: [ "https://www.unibet.com/betting/sports/filter/football" ]
  - stage: intelligent_explore
    args:
      - "football match links or event cards"
      - 2
  - stage: intelligent_flatSelect
    args:
      - "betting market sections with odds for different outcomes"
      - "Extract: event_name, event_date, market_type, selection, odds_decimal, odds_raw"
      - "unibet_"
  - stage: python_row_transform:normalize_unibet_intelligent
    args: []
  - stage: python_row_transform:add_metadata
    args:
      - bookmaker: "unibet"
        sport: "football"
        extraction_method: "intelligent"
  - stage: cache
    args: []
  - stage: store
    args: [ "unibet_offers" ]

  # ============================================
  # Step 5: Merge All Bookmakers
  # ============================================
  - stage: reset
    args: []
  - stage: union_with
    args: [ "bet365_offers", "pinnacle_offers", "betfair_offers", "williamhill_offers", "unibet_offers" ]

  # ============================================
  # Step 6: Normalize Event Names for Matching
  # Critical: Same event can have different names across bookmakers
  # ============================================
  - stage: python_row_transform:normalize_event_name
    args: []

  # ============================================
  # Step 7: Generate Event ID for Matching
  # Creates stable event_id from normalized event name + date
  # ============================================
  - stage: python_row_transform:generate_event_id
    args: []

  # ============================================
  # Step 8: Create Matching Key
  # Group by event_id + market_type + selection
  # ============================================
  - stage: python_row_transform:create_matching_key
    args: []

  # ============================================
  # Step 9: Aggregate Odds by Event
  # CRITICAL: Aggregate all odds for the same event/market/selection
  # before surebet detection
  # ============================================
  - stage: aggregation_group_by_key
    args:
      - key_field: "matching_key"
        aggregations:
          - field: "odds_decimal"
            type: "collect_list"
            as: "odds_by_bookmaker"
          - field: "bookmaker"
            type: "collect_list"
            as: "bookmakers"
          - field: "event_name_normalized"
            type: "first"
            as: "event_name_canonical"
          - field: "event_id"
            type: "first"
            as: "event_id"

  # ============================================
  # Step 10: Create Odds Comparison Table
  # Pivot odds by bookmaker for each event/market/selection
  # ============================================
  - stage: python_row_transform:create_odds_comparison_by_event
    args: []

  # ============================================
  # Step 11: Detect Surebet Opportunities
  # Consult aggregated odds by event to find arbitrage
  # ============================================
  - stage: python_row_transform:detect_surebet_by_event
    args:
      - min_profit_margin: 0.02  # Minimum 2% profit margin

  # ============================================
  # Step 12: Save Results
  # ============================================
  - stage: save_csv
    args: [ "${OUTPUT_PATH_SUREBET_OPPORTUNITIES}", "overwrite" ]
```

### Python Extensions for Intelligent Extraction Normalization

```python
# python_extensions:
#   stages:
#     normalize_bet365_intelligent:
#       type: row_transform
#       function: |
def normalize_bet365_intelligent(row):
    """Normalize odds extracted via intelligent_flatSelect from bet365."""
    # intelligent_flatSelect extracts fields with prefix "bet365_"
    odds_decimal = row.get("bet365_odds_decimal")
    odds_raw = row.get("bet365_odds_raw", "")
    
    # If odds_decimal is already a number, use it
    if odds_decimal:
        try:
            row["odds_decimal"] = float(odds_decimal)
        except:
            row["odds_decimal"] = None
    elif odds_raw:
        # Parse odds_raw if odds_decimal wasn't extracted
        # bet365 format: "2.50" or "3/2"
        try:
            if "/" in odds_raw:
                parts = odds_raw.split("/")
                decimal = (float(parts[0]) / float(parts[1])) + 1
                row["odds_decimal"] = round(decimal, 2)
            else:
                row["odds_decimal"] = float(odds_raw.replace(",", ""))
        except:
            row["odds_decimal"] = None
    
    # Map extracted fields to canonical schema
    row["event_name"] = row.get("bet365_event_name", "")
    row["event_date"] = row.get("bet365_event_date", "")
    row["market_type"] = row.get("bet365_market_type", "").lower().replace(" ", "_")
    row["selection"] = row.get("bet365_selection", "").lower().replace(" ", "_")
    row["url"] = row.get("_url", "")  # Current page URL
    
    return row

#     detect_surebet:
#       type: row_transform
#       function: |
def detect_surebet(row, min_profit_margin=0.02):
    """Detect surebet (arbitrage) opportunities for a market."""
    # For match_winner market with 3 outcomes
    # Collect all odds for this event+market from different bookmakers
    # This is a simplified version - in production, you'd group by event_id + market_type first
    
    # Example: if we have odds from multiple bookmakers in the same row (after pivot)
    odds_home = row.get("odds_home", 0) or 999
    odds_draw = row.get("odds_draw", 0) or 999
    odds_away = row.get("odds_away", 0) or 999
    
    # Find best odds for each outcome across all bookmakers
    bookmakers = ["bet365", "pinnacle", "betfair", "williamhill", "unibet"]
    
    best_home = min([row.get(f"{b}_odds_home", 999) for b in bookmakers if row.get(f"{b}_odds_home")])
    best_draw = min([row.get(f"{b}_odds_draw", 999) for b in bookmakers if row.get(f"{b}_odds_draw")])
    best_away = min([row.get(f"{b}_odds_away", 999) for b in bookmakers if row.get(f"{b}_odds_away")])
    
    # Calculate implied probability
    if best_home > 0 and best_draw > 0 and best_away > 0:
        implied_prob = (1/best_home) + (1/best_draw) + (1/best_away)
        
        # Surebet exists if implied_prob < 1.0
        if implied_prob < 1.0:
            profit_margin = (1.0 - implied_prob) * 100  # Percentage profit
            
            if profit_margin >= min_profit_margin * 100:
                row["surebet_exists"] = True
                row["surebet_profit_pct"] = profit_margin
                row["best_home_odds"] = best_home
                row["best_draw_odds"] = best_draw
                row["best_away_odds"] = best_away
            else:
                row["surebet_exists"] = False
                row["surebet_profit_pct"] = 0.0
        else:
            row["surebet_exists"] = False
            row["surebet_profit_pct"] = 0.0
    
    return row
```

### Why Intelligent Extraction is Better for Complex Tables

**Traditional CSS Selectors** often fail with:
- Dynamic content loaded via JavaScript
- Nested structures where odds are in different containers
- Non-standard HTML that doesn't follow predictable patterns
- Multiple market types mixed on the same page

**Intelligent Extraction** (`intelligent_flatSelect`) solves this by:
- Using LLM to understand the page structure semantically
- Adapting to different HTML layouts automatically
- Extracting structured data even from complex, nested tables
- Handling dynamic content that changes structure

### Critical: Event Matching Before Surebet Detection

**Important**: The surebet finder **must consult aggregated odds by event**. This means:

1. **Normalize event names** across bookmakers (e.g., "Man Utd vs Liverpool" = "Manchester United v Liverpool")
2. **Generate stable event_id** from normalized event name + date
3. **Aggregate all odds** for the same event/market/selection from all bookmakers
4. **Then detect surebet** by comparing aggregated odds across bookmakers

Without proper event matching, the same event might be treated as different events, preventing surebet detection.

### Example Output: Surebet Opportunities Table

The final output will contain rows with surebet opportunities:

| event_id | event_name | market_type | selection | bet365_odds | pinnacle_odds | betfair_odds | williamhill_odds | unibet_odds | best_odds | surebet_exists | surebet_profit_pct |
|----------|------------|-------------|-----------|-------------|---------------|--------------|------------------|-------------|-----------|----------------|-------------------|
| event_123 | Man Utd vs Liverpool | match_winner | home_win | 2.10 | 2.15 | 2.12 | 2.08 | 2.13 | 2.15 | False | 0.0 |
| event_123 | Man Utd vs Liverpool | match_winner | draw | 3.20 | 3.25 | 3.18 | 3.22 | 3.24 | 3.25 | False | 0.0 |
| event_124 | Arsenal vs Chelsea | match_winner | home_win | 2.50 | 2.55 | 2.48 | 2.52 | 2.51 | 2.55 | True | 2.3 |

## Arbitrage Detection

After creating the matching table, detect arbitrage opportunities:

```yaml
# Pipeline: Detect arbitrage opportunities
pipeline:
  - stage: load_csv
    args:
      - { path: "${OUTPUT_PATH_MATCHING_TABLE}", header: "true", inferSchema: "true" }
  
  # Calculate arbitrage for each market
  - stage: python_row_transform:calculate_arbitrage
    args: []
  
  # Filter only profitable arbitrage opportunities
  - stage: python_row_transform:filter_arbitrage
    args:
      - min_profit_margin: 0.02  # Minimum 2% profit margin
  
  - stage: save_csv
    args: [ "${OUTPUT_PATH_ARBITRAGE_OPPORTUNITIES}", "overwrite" ]
```

```python
# python_extensions:
#   stages:
#     calculate_arbitrage:
#       type: row_transform
#       function: |
def calculate_arbitrage(row):
    """Calculate arbitrage opportunity for a market."""
    # For match_winner market with 3 outcomes (home, draw, away)
    odds_home = row.get("bet365_home", 0) or row.get("pinnacle_home", 0) or 999
    odds_draw = row.get("bet365_draw", 0) or row.get("pinnacle_draw", 0) or 999
    odds_away = row.get("bet365_away", 0) or row.get("pinnacle_away", 0) or 999
    
    # Find best odds for each outcome
    best_home = min([row.get(f"{b}_home", 999) for b in ["bet365", "pinnacle", "betfair", "williamhill", "unibet"] if row.get(f"{b}_home")])
    best_draw = min([row.get(f"{b}_draw", 999) for b in ["bet365", "pinnacle", "betfair", "williamhill", "unibet"] if row.get(f"{b}_draw")])
    best_away = min([row.get(f"{b}_away", 999) for b in ["bet365", "pinnacle", "betfair", "williamhill", "unibet"] if row.get(f"{b}_away")])
    
    # Calculate implied probability
    implied_prob = (1/best_home) + (1/best_draw) + (1/best_away)
    
    # Arbitrage exists if implied_prob < 1.0
    if implied_prob < 1.0:
        row["arbitrage_exists"] = True
        row["arbitrage_profit"] = (1.0 - implied_prob) * 100  # Percentage profit
    else:
        row["arbitrage_exists"] = False
        row["arbitrage_profit"] = 0.0
    
    return row
```

## API Endpoints for Odds Comparison

After processing, query the unified odds dataset:

#### Get Best Odds for an Event

```http
GET /api/webrobot/api/datasets/{datasetId}/query?sqlQuery=SELECT event_name, selection, MAX(odds_decimal) as best_odds, bookmaker FROM odds_table WHERE event_id = 'event_123' GROUP BY event_name, selection, bookmaker
```

#### Get Arbitrage Opportunities

```http
GET /api/webrobot/api/datasets/{datasetId}/query?sqlQuery=SELECT * FROM arbitrage_table WHERE arbitrage_profit > 2.0 ORDER BY arbitrage_profit DESC
```


