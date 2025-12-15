---
title: Portfolio Management & 90-Day Asset Prediction
version: 1.0.0
description: "Complete guide for building training datasets for 90-day asset price prediction models using WebRobot ETL pipelines, designed for LLM fine-tuning on NVIDIA DGX SPARK"
---

# Portfolio Management & 90-Day Asset Prediction

This guide demonstrates how to use WebRobot ETL to build **production-ready training datasets for 90-day asset price prediction models**, designed for fine-tuning Large Language Models (LLMs) on NVIDIA DGX SPARK infrastructure. This is part of the **Feeless portfolio management layer** for agentic pools.

## Business Use Case

**Goal**: Build comprehensive training datasets for predicting asset prices 90 days into the future by:

- **Aggregating multi-source data**: Historical prices, technical indicators, macroeconomic data, news sentiment, and alternative data
- **Feature engineering**: Calculating technical indicators (RSI, MACD, Bollinger Bands), returns, volatility, and macro correlations
- **Target generation**: Computing actual 90-day forward returns and price movements
- **Formatting for LLM fine-tuning**: Structuring data into time-series prediction format compatible with instruction-following models
- **Export for NVIDIA DGX SPARK**: Generating a CSV training dataset (convert to JSONL/Parquet downstream as needed)

**Key Challenges**:
- **Multi-asset coverage**: Support equity, crypto, bonds, commodities, FX
- **Time-series alignment**: Synchronize data from multiple sources with different frequencies
- **Feature engineering**: Calculate 50+ technical and fundamental features
- **Data quality**: Handle missing data, outliers, and data gaps
- **Format optimization**: Structure for LLM fine-tuning (instruction-following with temporal context)

## Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Price Data  │     │ Macro Data  │     │ News/Sent.  │     │ Alternative │
│ (Alpha V.)  │     │ (FRED)      │     │ (GDELT)     │     │ (Social)    │
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
                    │  Feature    │
                    │ Engineering │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Calculate  │
                    │ 90d Target  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Format for │
                    │ LLM SFT     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Export     │
                    │  (CSV)      │
                    └─────────────┘
```

## Canonical Training Dataset Schema

### Core Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | ISO 8601 | Observation date | `2024-01-15T00:00:00Z` |
| `asset_symbol` | String | Asset identifier | `BTC-USD`, `AAPL`, `EURUSD` |
| `asset_class` | String | Asset category | `crypto`, `equity`, `fx`, `commodity` |
| `price_close` | Float | Closing price | `45000.50` |
| `volume` | Float | Trading volume | `1250000.0` |
| `target_price_90d` | Float | Actual price 90 days later | `48500.25` |
| `target_return_90d` | Float | Actual return (log) | `0.0745` |
| `target_return_pct_90d` | Float | Actual return (%) | `7.45` |

### Technical Indicators

| Field | Type | Description |
|-------|------|-------------|
| `rsi_14` | Float | RSI (14-period) |
| `macd` | Float | MACD line |
| `macd_signal` | Float | MACD signal line |
| `macd_histogram` | Float | MACD histogram |
| `bb_upper` | Float | Bollinger Bands upper |
| `bb_middle` | Float | Bollinger Bands middle (SMA) |
| `bb_lower` | Float | Bollinger Bands lower |
| `sma_20` | Float | Simple Moving Average (20) |
| `sma_50` | Float | Simple Moving Average (50) |
| `sma_200` | Float | Simple Moving Average (200) |
| `ema_12` | Float | Exponential Moving Average (12) |
| `ema_26` | Float | Exponential Moving Average (26) |
| `volatility_30d` | Float | 30-day volatility (annualized) |
| `volatility_60d` | Float | 60-day volatility (annualized) |
| `volatility_90d` | Float | 90-day volatility (annualized) |
| `momentum_5d` | Float | 5-day momentum |
| `momentum_10d` | Float | 10-day momentum |
| `momentum_30d` | Float | 30-day momentum |
| `atr_14` | Float | Average True Range (14) |
| `adx_14` | Float | ADX (14) |

### Macroeconomic Features

| Field | Type | Description |
|-------|------|-------------|
| `sp500_close` | Float | S&P 500 closing price |
| `vix` | Float | VIX volatility index |
| `dxy` | Float | US Dollar Index |
| `us10y_yield` | Float | US 10-year Treasury yield |
| `us2y_yield` | Float | US 2-year Treasury yield |
| `gold_price` | Float | Gold price (USD/oz) |
| `oil_price` | Float | WTI crude oil price |
| `cpi_yoy` | Float | CPI year-over-year change |
| `gdp_growth_qoq` | Float | GDP growth quarter-over-quarter |
| `unemployment_rate` | Float | Unemployment rate |

### Sentiment & Alternative Data

| Field | Type | Description |
|-------|------|-------------|
| `news_sentiment_score` | Float | Aggregated news sentiment (-1 to 1) |
| `news_volume` | Integer | Number of news articles |
| `social_sentiment_score` | Float | Social media sentiment (-1 to 1) |
| `social_mention_count` | Integer | Social media mentions |
| `google_trends_score` | Float | Google Trends interest (normalized) |
| `fear_greed_index` | Float | Crypto Fear & Greed Index (0-100) |

### LLM Fine-Tuning Format Fields

| Field | Type | Description |
|-------|------|-------------|
| `instruction` | String | Prediction prompt with context |
| `input` | String | JSON string of features |
| `output` | String | Target prediction (price/return) |
| `context_window` | Array | Historical context (last N days) |

## Python Extensions

### Complete Python Extensions Implementation

```python
# python_extensions:
#   stages:
#     parse_alphavantage_crypto:
#       type: row_transform
#       function: |
def parse_alphavantage_crypto(row):
    """
    Parse Alpha Vantage crypto JSON response into structured format.
    """
    import json
    import pandas as pd
    from datetime import datetime
    
    price_json = row.get("price_json")
    if not price_json:
        return row
    
    try:
        data = json.loads(price_json)
        time_series = data.get("Time Series (Digital Currency Daily)", {})
        
        records = []
        for date_str, values in time_series.items():
            records.append({
                "timestamp": pd.to_datetime(date_str).isoformat(),
                "price_open": float(values.get("1a. open (USD)", 0)),
                "price_high": float(values.get("2a. high (USD)", 0)),
                "price_low": float(values.get("3a. low (USD)", 0)),
                "price_close": float(values.get("4a. close (USD)", 0)),
                "volume": float(values.get("5. volume", 0)),
                "market_cap": float(values.get("6. market cap (USD)", 0)),
            })
        
        # Sort by date
        records.sort(key=lambda x: x["timestamp"])
        row["price_records"] = records
        row["price_data"] = records[-1] if records else {}
        
    except Exception as e:
        row["parse_error"] = str(e)
    
    return row

#     calculate_returns:
#       type: row_transform
#       function: |
def calculate_returns(row):
    """
    Calculate log returns and percentage returns.
    """
    import numpy as np
    
    price_records = row.get("price_records", [])
    if len(price_records) < 2:
        return row
    
    current_price = price_records[-1].get("price_close")
    previous_price = price_records[-2].get("price_close") if len(price_records) > 1 else current_price
    
    if current_price and previous_price and previous_price > 0:
        row["return_1d"] = np.log(current_price / previous_price)
        row["return_1d_pct"] = ((current_price / previous_price) - 1) * 100
    
    return row

#     calculate_technical_indicators:
#       type: row_transform
#       function: |
def calculate_technical_indicators(row, window=14):
    """
    Calculate RSI, MACD, Bollinger Bands, and other technical indicators.
    Requires historical price data in context_window.
    """
    import numpy as np
    
    prices = row.get("context_window", [])
    if len(prices) < window:
        return row
    
    # RSI calculation
    deltas = np.diff(prices[-window:])
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gains)
    avg_loss = np.mean(losses)
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    row["rsi_14"] = rsi
    
    # MACD calculation (simplified)
    ema_12 = np.mean(prices[-12:])
    ema_26 = np.mean(prices[-26:]) if len(prices) >= 26 else ema_12
    macd = ema_12 - ema_26
    row["macd"] = macd
    row["macd_signal"] = np.mean([macd] * 9)  # Simplified signal
    row["macd_histogram"] = macd - row["macd_signal"]
    
    # Bollinger Bands
    sma_20 = np.mean(prices[-20:])
    std_20 = np.std(prices[-20:])
    row["bb_upper"] = sma_20 + (2 * std_20)
    row["bb_middle"] = sma_20
    row["bb_lower"] = sma_20 - (2 * std_20)
    
    # Moving averages
    row["sma_20"] = np.mean(prices[-20:])
    row["sma_50"] = np.mean(prices[-50:]) if len(prices) >= 50 else sma_20
    row["sma_200"] = np.mean(prices[-200:]) if len(prices) >= 200 else sma_20
    
    # Volatility (annualized)
    returns = np.diff(prices[-30:]) / prices[-30:-1]
    row["volatility_30d"] = np.std(returns) * np.sqrt(252)  # Annualized
    
    return row

#     calculate_90d_target:
#       type: row_transform
#       function: |
def calculate_90d_target(row, future_prices):
    """
    Calculate 90-day forward target (price and return).
    Requires future price data to compute actual targets.
    """
    current_price = row.get("price_close")
    if not current_price or not future_prices:
        return row
    
    # Find price 90 days ahead
    target_price = future_prices.get("price_close_90d")
    if target_price:
        row["target_price_90d"] = target_price
        row["target_return_90d"] = np.log(target_price / current_price)
        row["target_return_pct_90d"] = ((target_price / current_price) - 1) * 100
    
    return row

#     format_for_llm_finetuning:
#       type: row_transform
#       function: |
def format_for_llm_finetuning(row, asset_symbol="BTC-USD"):
    """
    Format row into instruction-following format for LLM fine-tuning.
    Compatible with Alpaca/ShareGPT style.
    """
    import json
    
    # Build instruction with context
    instruction = f"""Predict the 90-day forward price and return for {asset_symbol} based on the following technical, macroeconomic, and sentiment features."""
    
    # Extract features as JSON
    features = {
        "price_close": row.get("price_close"),
        "rsi_14": row.get("rsi_14"),
        "macd": row.get("macd"),
        "bb_upper": row.get("bb_upper"),
        "bb_lower": row.get("bb_lower"),
        "volatility_30d": row.get("volatility_30d"),
        "sp500_close": row.get("sp500_close"),
        "vix": row.get("vix"),
        "news_sentiment_score": row.get("news_sentiment_score"),
        "social_sentiment_score": row.get("social_sentiment_score"),
    }
    
    # Build output (target prediction)
    output = json.dumps({
        "predicted_price_90d": row.get("target_price_90d"),
        "predicted_return_90d": row.get("target_return_90d"),
        "predicted_return_pct_90d": row.get("target_return_pct_90d"),
    })
    
    row["instruction"] = instruction
    row["input"] = json.dumps(features)
    row["output"] = output
    
    return row

#     parse_fred_series:
#       type: row_transform
#       function: |
def parse_fred_series(row, series_id="SP500", field_name="sp500_close"):
    """
    Parse FRED API JSON response into time series.
    """
    import json
    import pandas as pd
    
    json_field = f"{series_id.lower()}_json"
    json_data = row.get(json_field)
    if not json_data:
        return row
    
    try:
        data = json.loads(json_data)
        observations = data.get("observations", [])
        
        records = []
        for obs in observations:
            date_str = obs.get("date")
            value_str = obs.get("value")
            if date_str and value_str and value_str != ".":
                try:
                    records.append({
                        "timestamp": pd.to_datetime(date_str).isoformat(),
                        field_name: float(value_str),
                    })
                except (ValueError, TypeError):
                    continue
        
        records.sort(key=lambda x: x["timestamp"])
        row["fred_records"] = records
        row[field_name] = records[-1].get(field_name) if records else None
        
    except Exception as e:
        row["parse_error"] = str(e)
    
    return row

#     parse_gdelt_news:
#       type: row_transform
#       function: |
def parse_gdelt_news(row):
    """
    Parse GDELT news API response.
    """
    import json
    import pandas as pd
    
    news_json = row.get("news_json")
    if not news_json:
        return row
    
    try:
        data = json.loads(news_json)
        articles = data.get("articles", [])
        
        records = []
        for article in articles:
            records.append({
                "timestamp": pd.to_datetime(article.get("date", "")).isoformat() if article.get("date") else None,
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                "tone": float(article.get("tone", 0)),  # GDELT tone score
                "source": article.get("source", ""),
            })
        
        row["news_records"] = records
        
    except Exception as e:
        row["parse_error"] = str(e)
    
    return row

#     calculate_news_sentiment:
#       type: row_transform
#       function: |
def calculate_news_sentiment(row, sentiment_field="tone", normalize=True):
    """
    Calculate aggregated news sentiment score.
    """
    news_records = row.get("news_records", [])
    if not news_records:
        return row
    
    # GDELT tone is already normalized (-100 to +100)
    tones = [r.get(sentiment_field, 0) for r in news_records if r.get(sentiment_field) is not None]
    
    if tones:
        if normalize:
            # Normalize to -1 to 1
            row["news_sentiment_score"] = (sum(tones) / len(tones)) / 100.0
        else:
            row["news_sentiment_score"] = sum(tones) / len(tones)
        row["news_volume"] = len(tones)
    
    return row

# Optional (recommended for compliance): ingest pre-scored social sentiment from a licensed feed.
# Expect CSV fields like: timestamp, social_sentiment_score, social_mention_count
#
#     normalize_social_sentiment_daily:
#       type: row_transform
#       function: |
def normalize_social_sentiment_daily(row):
    """Normalize pre-scored daily social sentiment rows loaded from CSV."""
    # Ensure types are consistent
    try:
        if row.get("social_sentiment_score") is not None:
            row["social_sentiment_score"] = float(row["social_sentiment_score"])
    except (ValueError, TypeError):
        row["social_sentiment_score"] = None
    try:
        if row.get("social_mention_count") is not None:
            row["social_mention_count"] = int(float(row["social_mention_count"]))
    except (ValueError, TypeError):
        row["social_mention_count"] = None
    return row

#     aggregate_sentiment_by_date:
#       type: row_transform
#       function: |
def aggregate_sentiment_by_date(row, date_field="timestamp", window=1, aggregation="mean"):
    """
    Aggregate sentiment scores by date (daily, weekly, etc.).
    """
    import pandas as pd
    from collections import defaultdict
    
    records = row.get("news_records", [])
    if not records:
        return row
    
    # Group by date
    date_sentiment = defaultdict(list)
    for record in records:
        date = record.get(date_field)
        if date:
            date_key = pd.to_datetime(date).date().isoformat()
            sentiment = record.get("news_sentiment_score") or record.get("social_sentiment_score")
            if sentiment is not None:
                date_sentiment[date_key].append(sentiment)
    
    # Aggregate
    aggregated = {}
    for date, sentiments in date_sentiment.items():
        if aggregation == "mean":
            aggregated[date] = sum(sentiments) / len(sentiments)
        elif aggregation == "median":
            aggregated[date] = sorted(sentiments)[len(sentiments) // 2]
        elif aggregation == "sum":
            aggregated[date] = sum(sentiments)
    
    row["sentiment_by_date"] = aggregated
    return row

#     parse_coingecko_market_chart:
#       type: row_transform
#       function: |
def parse_coingecko_market_chart(row):
    """
    Parse CoinGecko market chart API response.
    """
    import json
    import pandas as pd
    
    coingecko_json = row.get("coingecko_json")
    if not coingecko_json:
        return row
    
    try:
        data = json.loads(coingecko_json)
        prices = data.get("prices", [])
        market_caps = data.get("market_caps", [])
        volumes = data.get("total_volumes", [])
        
        records = []
        for i, price_data in enumerate(prices):
            timestamp_ms = price_data[0]
            price = price_data[1]
            market_cap = market_caps[i][1] if i < len(market_caps) else None
            volume = volumes[i][1] if i < len(volumes) else None
            
            records.append({
                "timestamp": pd.to_datetime(timestamp_ms, unit="ms").isoformat(),
                "price_close": price,
                "market_cap": market_cap,
                "volume_24h": volume,
            })
        
        records.sort(key=lambda x: x["timestamp"])
        row["coingecko_records"] = records
        
    except Exception as e:
        row["parse_error"] = str(e)
    
    return row

#     align_time_series:
#       type: row_transform
#       function: |
def align_time_series(row, date_field="timestamp", frequency="daily", method="forward_fill"):
    """
    Align time series data from multiple sources to common frequency.
    """
    import pandas as pd
    
    # This would typically be done at the DataFrame level in Spark
    # For row_transform, we ensure date field is properly formatted
    timestamp = row.get(date_field)
    if timestamp:
        try:
            dt = pd.to_datetime(timestamp)
            row[date_field] = dt.isoformat()
            row["date"] = dt.date().isoformat()
            row["year"] = dt.year
            row["month"] = dt.month
            row["day"] = dt.day
        except Exception as e:
            row["date_parse_error"] = str(e)
    
    return row

#     calculate_90d_target:
#       type: row_transform
#       function: |
def calculate_90d_target(row, price_field="price_close", future_days=90):
    """
    Calculate 90-day forward target from price records.
    This requires the full time series to be available.
    """
    import pandas as pd
    
    price_records = row.get("price_records", [])
    if len(price_records) < future_days:
        return row
    
    current_timestamp = pd.to_datetime(row.get("timestamp"))
    current_price = row.get(price_field)
    
    if not current_price or not current_timestamp:
        return row
    
    # Find price 90 days ahead
    target_date = current_timestamp + pd.Timedelta(days=future_days)
    
    # Find closest record to target date
    target_price = None
    for record in price_records:
        record_date = pd.to_datetime(record.get("timestamp"))
        if record_date >= target_date:
            target_price = record.get(price_field)
            break
    
    if target_price:
        row["target_price_90d"] = target_price
        row["target_return_90d"] = np.log(target_price / current_price)
        row["target_return_pct_90d"] = ((target_price / current_price) - 1) * 100
    
    return row

#     enrich_with_macro_correlations:
#       type: row_transform
#       function: |
def enrich_with_macro_correlations(row, correlation_window=30):
    """
    Calculate correlations with macroeconomic indicators.
    """
    # This would typically require window functions in Spark
    # For row_transform, we just ensure macro fields are present
    macro_fields = ["sp500_close", "vix", "us10y_yield", "gold_price"]
    for field in macro_fields:
        if field not in row:
            row[field] = None
    
    return row

#     fill_missing_values:
#       type: row_transform
#       function: |
def fill_missing_values(row, method="forward_fill", limit=7):
    """
    Fill missing values using forward fill or other methods.
    Note: This is simplified; full implementation would use window functions.
    """
    # For row_transform, we just ensure critical fields have defaults
    critical_fields = {
        "rsi_14": 50.0,
        "macd": 0.0,
        "volatility_30d": 0.0,
        "news_sentiment_score": 0.0,
        "social_sentiment_score": 0.0,
    }
    
    for field, default_value in critical_fields.items():
        if field not in row or row[field] is None:
            row[field] = default_value
    
    return row

#     normalize_features:
#       type: row_transform
#       function: |
def normalize_features(row, method="standardize", exclude_fields=None):
    """
    Normalize features (standardization, min-max, etc.).
    Note: Full normalization requires dataset-level statistics.
    """
    exclude_fields = exclude_fields or []
    
    # For row_transform, we ensure numeric fields are properly typed
    numeric_fields = [
        "price_close", "rsi_14", "macd", "bb_upper", "bb_lower",
        "volatility_30d", "sp500_close", "vix", "news_sentiment_score"
    ]
    
    for field in numeric_fields:
        if field not in exclude_fields and field in row:
            try:
                row[field] = float(row[field]) if row[field] is not None else None
            except (ValueError, TypeError):
                row[field] = None
    
    return row

#     validate_training_dataset:
#       type: row_transform
#       function: |
def validate_training_dataset(row):
    """
    Validate training dataset quality.
    """
    required_fields = [
        "timestamp", "asset_symbol", "price_close",
        "target_price_90d", "target_return_90d",
        "rsi_14", "macd", "volatility_30d"
    ]
    
    for field in required_fields:
        if field not in row or row[field] is None:
            row["validation_error"] = f"Missing required field: {field}"
            row["validation_status"] = "invalid"
            return row
    
    # Validate target exists
    if row["target_price_90d"] <= 0:
        row["validation_error"] = "Invalid target_price_90d"
        row["validation_status"] = "invalid"
        return row
    
    # Validate RSI range
    if row["rsi_14"] < 0 or row["rsi_14"] > 100:
        row["validation_error"] = "Invalid RSI_14 range"
        row["validation_status"] = "invalid"
        return row
    
    row["validation_status"] = "valid"
    return row
```

## Concrete Example: 90-Day BTC Prediction Training Set

### Data Sources

1. **Price Data**: Alpha Vantage API (crypto daily OHLCV)
2. **Macro Data**: FRED API (S&P 500, VIX, Treasury yields)
3. **News Sentiment**: GDELT Project (news events, sentiment)
4. **Social Sentiment**: Licensed social sentiment feed (pre-curated daily CSV)
5. **Alternative Data**: CoinGecko API (Fear & Greed Index, market cap)

### Pipeline Architecture

```yaml
# ============================================
# Source 1: Historical Price Data (Alpha Vantage)
# ============================================
fetch:
  url: "https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=BTC&market=USD&apikey=${ALPHAVANTAGE_API_KEY}"

pipeline:
  # Extract historical prices
  - stage: extract
    args:
      - { selector: "pre", method: "text", as: "price_json" }
  - stage: python_row_transform:parse_alphavantage_crypto
    args: []
  - stage: python_row_transform:calculate_technical_indicators
    args:
      - window: 14
  - stage: cache
    args: []
  - stage: store
    args: [ "price_data" ]

  # ============================================
  # Source 2: Macroeconomic Data (FRED API)
  # ============================================
  - stage: reset
    args: []
  - stage: visit
    args: [ "https://api.stlouisfed.org/fred/series/observations?series_id=SP500&api_key=${FRED_API_KEY}&file_type=json" ]
  - stage: extract
    args:
      - { selector: "pre", method: "text", as: "macro_json" }
  - stage: python_row_transform:parse_fred_data
    args: []
  - stage: python_row_transform:enrich_with_macro
    args:
      - indicators: ["SP500", "VIXCLS", "DGS10", "DGS2", "GOLDAMGBD228NLBM", "DCOILWTICO"]
  - stage: cache
    args: []
  - stage: store
    args: [ "macro_data" ]

  # ============================================
  # Source 3: News Sentiment (GDELT)
  # ============================================
  - stage: reset
    args: []
  - stage: visit
    args: [ "https://api.gdeltproject.org/api/v2/doc/doc?query=bitcoin%20OR%20BTC&mode=artlist&format=json&timespan=90d" ]
  - stage: extract
    args:
      - { selector: "pre", method: "text", as: "news_json" }
  - stage: python_row_transform:parse_gdelt_news
    args: []
  - stage: python_row_transform:calculate_news_sentiment
    args: []
  - stage: python_row_transform:aggregate_sentiment_by_date
    args:
      - window: 1  # Daily aggregation
  - stage: cache
    args: []
  - stage: store
    args: [ "news_sentiment" ]

  # ============================================
  # Source 4: Social sentiment (licensed provider / customer-owned feed)
  # ============================================
  - stage: reset
    args: []
  - stage: load_csv
    args:
      - { path: "${SOCIAL_SENTIMENT_DAILY_CSV_PATH}", header: "true", inferSchema: "true" }
  - stage: cache
    args: []
  - stage: store
    args: [ "social_sentiment" ]

  # ============================================
  # Source 5: Alternative Data (CoinGecko)
  # ============================================
  - stage: reset
    args: []
  - stage: visit
    args: [ "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true" ]
  - stage: extract
    args:
      - { selector: "pre", method: "text", as: "coingecko_json" }
  - stage: python_row_transform:parse_coingecko_data
    args: []
  - stage: cache
    args: []
  - stage: store
    args: [ "alternative_data" ]

  # ============================================
  # Union All Sources
  # ============================================
  - stage: union_with
    args: [ "price_data" ]
  - stage: union_with
    args: [ "macro_data" ]
  - stage: union_with
    args: [ "news_sentiment" ]
  - stage: union_with
    args: [ "social_sentiment" ]
  - stage: union_with
    args: [ "alternative_data" ]

  # ============================================
  # Time-Series Alignment & Feature Engineering
  # ============================================
  - stage: python_row_transform:align_time_series
    args:
      - date_field: "timestamp"
      - frequency: "daily"
  - stage: python_row_transform:calculate_90d_target
    args: []
  - stage: python_row_transform:fill_missing_values
    args:
      - method: "forward_fill"
  - stage: python_row_transform:format_for_llm_finetuning
    args:
      - asset_symbol: "BTC-USD"
  - stage: dedup
    args: [ "timestamp", "asset_symbol" ]

  # ============================================
  # Export (CSV)
  # ============================================
  - stage: save_csv
    args: [ "${OUTPUT_PATH_TRAINSET_CSV}", "overwrite" ]
```

## LLM Fine-Tuning Format (Instruction fields in CSV)

### Instruction-Following Format (Alpaca style, stored as CSV columns)

```json
{
  "instruction": "Predict the 90-day forward price and return for BTC-USD based on the following technical, macroeconomic, and sentiment features.",
  "input": "{\"price_close\": 45000.50, \"rsi_14\": 65.2, \"macd\": 125.5, \"bb_upper\": 47000.0, \"bb_lower\": 43000.0, \"volatility_30d\": 0.45, \"sp500_close\": 4500.25, \"vix\": 18.5, \"news_sentiment_score\": 0.15, \"social_sentiment_score\": 0.22}",
  "output": "{\"predicted_price_90d\": 48500.25, \"predicted_return_90d\": 0.0745, \"predicted_return_pct_90d\": 7.45}"
}
```

### Time-Series Context Format

```json
{
  "instruction": "Predict the 90-day forward return for BTC-USD given the historical price context.",
  "input": "{\"context_window\": [42000, 43000, 44000, 45000, 44500, 45000, 45500], \"current_price\": 45000.50, \"rsi_14\": 65.2, \"volatility_30d\": 0.45}",
  "output": "{\"predicted_return_90d\": 0.0745, \"predicted_return_pct_90d\": 7.45}"
}
```

## Integration with NVIDIA DGX SPARK

### Dataset Requirements

- **Format**: CSV (columns: `instruction`, `input`, `output`)
- **Size**: Optimized for distributed training (shardable)
- **Schema**: Consistent across all records
- **Partitioning**: By date range for efficient loading

### Training Pipeline

```bash
# Example: Load dataset into Spark for distributed training
spark-submit \
  --master spark://dgx-cluster:7077 \
  --conf spark.executor.memory=64g \
  --conf spark.executor.cores=16 \
  --class com.webrobot.llm.TrainingPipeline \
  webrobot-llm-training.jar \
  --input ${OUTPUT_PATH_TRAINSET_CSV} \
  --output s3://webrobot-data/portfolio-management/models/btc-90d-predictor \
  --model-path /models/llama2-7b \
  --format instruction_following
```

## Quality Metrics & Validation

### Dataset Quality Checks

1. **Completeness**: Ensure >95% of dates have all required features
2. **Target Coverage**: Verify 90-day forward targets exist for all training samples
3. **Feature Distribution**: Check for outliers and normalize if needed
4. **Temporal Consistency**: Ensure no gaps >7 days in time series
5. **Correlation Analysis**: Validate feature-target correlations

### Validation Steps

```python
# python_extensions:
#   stages:
#     validate_training_dataset:
#       type: row_transform
#       function: |
def validate_training_dataset(row):
    """
    Validate training dataset quality.
    """
    required_fields = [
        "timestamp", "asset_symbol", "price_close",
        "target_price_90d", "target_return_90d",
        "rsi_14", "macd", "volatility_30d"
    ]
    
    for field in required_fields:
        if field not in row or row[field] is None:
            row["validation_error"] = f"Missing required field: {field}"
            return row
    
    # Validate target exists
    if row["target_price_90d"] <= 0:
        row["validation_error"] = "Invalid target_price_90d"
        return row
    
    # Validate RSI range
    if row["rsi_14"] < 0 or row["rsi_14"] > 100:
        row["validation_error"] = "Invalid RSI_14 range"
        return row
    
    row["validation_status"] = "valid"
    return row
```

## Multi-Asset Extension

To extend to multiple assets (equity, crypto, FX, commodities):

1. **Loop over asset symbols** in pipeline
2. **Normalize asset-specific features** (e.g., crypto vs equity metrics)
3. **Unify schema** across asset classes
4. **Add asset_class field** for model conditioning

## Next Steps

1. **Validate pipeline** with real data sources
2. **Generate training set** for target asset (e.g., BTC-USD)
3. **Fine-tune LLM** on NVIDIA DGX SPARK
4. **Evaluate model** on held-out test set
5. **Deploy for inference** in Feeless portfolio management layer

## Related Guides

- [LLM Fine-Tuning Dataset Construction](./vertical-llm-finetuning.md) - General LLM dataset building
- [Pipeline Stages Reference](./pipeline-stages.md) - Complete stage documentation
- [Vertical Use Cases Overview](./vertical-use-cases.md) - Other vertical examples

