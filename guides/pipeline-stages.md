---
title: Pipeline Stages Reference
version: 1.0.0
description: Complete reference of pipeline stages, YAML syntax, attribute resolvers, custom actions, and Python extensions
---

# Pipeline Stages Reference

Complete reference of pipeline stages, their YAML syntax, configuration options, and extension mechanisms.

## Stage Types Overview

Pipeline stages are categorized into:
- **Core Stages**: Basic data extraction and navigation
- **Intelligent Stages**: LLM-powered stages for adaptive extraction
- **Utility Stages**: Specialized processing stages
- **Use-Case Stages**: Domain-specific stages
- **Python Extensions**: Custom Python stages

### YAML constraints (important)

- Each `pipeline` entry must be a mapping with **only**:
  - `stage` (string)
  - `args` (array, optional)
- Extra keys on a stage item (for example `name`, `when`, etc.) are **not supported** by the Scala YAML parser and will fail parsing.

### Stage name resolution (important)

Stage lookup is case-insensitive and tolerant to underscores: `visitJoin`, `visit_join`, and `visitjoin` resolve to the same registered stage.

## Core Stages

### 1. Explore

**Purpose**: Breadth-first link discovery and crawling

**YAML Syntax:**
```yaml
pipeline:
  - stage: explore
    args: [ "a.category-link", 2 ]  # selector, depth
```

**Arguments:**
- `selector` (String): CSS selector for links (or a `$column` reference)
- `depth` (Int, optional): Maximum depth to crawl (default: `1`)

**Example:**
```yaml
pipeline:
  - stage: explore
    args: [ "a.category", 3 ]
```

---

### 2. Join

**Purpose**: Follow links for each row using HTTP (wget)

**YAML Syntax:**
```yaml
pipeline:
  - stage: join
    args: [ "a.product-link", "LeftOuter" ]  # selector, optional joinType
```

**Arguments:**
- `selector` (String): CSS selector for links (or a `$column` reference)
- `joinType` (String, optional): `Inner` or `LeftOuter` (default: `LeftOuter`)

**Example:**
```yaml
pipeline:
  - stage: join
    args: [ "a.detail-link", "Inner" ]
```

---

### 3. WgetJoin

**Purpose**: Follow links using the `wgetJoin(...)` primitive.

**YAML Syntax:**
```yaml
pipeline:
  - stage: wgetJoin  # also works as wget_join
    args: [ "a.detail-link", "LeftOuter" ]
```

**Arguments:**
- `selector` (String): CSS selector for links (or a `$column` reference)
- `joinType` (String, optional): `Inner` or `LeftOuter` (default: `LeftOuter`)

---

### 4. WgetExplore

**Purpose**: Breadth-first crawling using the `wgetExplore(...)` primitive.

**YAML Syntax:**
```yaml
pipeline:
  - stage: wgetExplore  # also works as wget_explore
    args: [ "li.next a", 2 ]
```

**Arguments:**
- `selector` (String): CSS selector for links (or a `$column` reference)
- `depth` (Int, optional): Maximum depth to crawl (default: `1`)

---

### 5. Extract

**Purpose**: Extract fields using selector-map configuration

**YAML Syntax:**
```yaml
pipeline:
  - stage: extract
    args:
      - { selector: "CSS_SELECTOR", method: "METHOD", as: "COLUMN_NAME" }
      - { selector: "...", method: "...", args: [...], as: "..." }
```

**Selector-Map Structure:**
```yaml
- selector: "span.price"        # Required: CSS selector
  method: "price"               # Required: extraction method
  as: "price_numeric"           # Optional: output column alias
```

**Example:**
```yaml
pipeline:
  - stage: extract
    args:
      - { selector: "h1", method: "text", as: "title" }
      - { selector: "span.price", method: "price", as: "price_numeric" }
      - { selector: "a", method: "attr:href", as: "link" }
```

---

### 6. FlatSelect

**Purpose**: Segment HTML block and create one row per segment (one row per repeated element). Requires `example-plugin`.

**YAML Syntax:**
```yaml
pipeline:
  - stage: flatSelect
    args:
      - "div.product"                   # segment selector
      -                                # extractors applied inside each segment (relative selectors)
        - { selector: "h3", method: "text", as: "name" }
        - { selector: ".price", method: "text", as: "price_raw" }
        - { selector: "img", method: "attr(src)", as: "img_src" }
```

**Arguments:**
- `segmentSelector` (String): CSS selector used to split the page into segments
- `extractors` (List[Map]): extractor maps applied to each segment (selectors are **relative**)

**Example:**
```yaml
pipeline:
  - stage: flatSelect
    args:
      - "div.product-item"
      - - { selector: "h3", method: "text", as: "product_name" }
        - { selector: ".price", method: "text", as: "price_raw" }
```

---

## Intelligent Stages (LLM-powered)

### Selector inference caching + template recognition (RoadRunner)

The Intelligent stages reduce repeated LLM calls by caching *inferred selectors* at **template-cluster level**:

- **Template fingerprint**: the HTML is fingerprinted (SimHash) and assigned to a *cluster* (layout template).
- **Cache key**: `(namespace, clusterId, kind, promptHash)`.
- **RoadRunner prepopulation**: on cache miss (or to improve generic selectors), we record HTML samples for the cluster and run **RoadRunner template induction** to draft a stable wrapper selector. This draft can later be validated/overridden by the LLM inference pipeline.

This is implemented in the core template layer (`SelectorResolver` + `RoadRunnerPrepopulator`) and used by stages like `intelligent_flatSelect` and `iextract`.

### 1. Intelligent Explore

**Purpose**: Like `explore`, but uses LLM to infer selector from natural language prompt

**YAML Syntax:**
```yaml
pipeline:
  - stage: intelligent_explore
    args: [ "category links", 2 ]  # prompt, depth
```

**Example:**
```yaml
pipeline:
  - stage: intelligent_explore
    args: [ "navigation menu items", 1 ]
```

---

### 2. Intelligent Join

**Purpose**: Join with inferred selector (PTA/LLM) + inferred actions

**YAML Syntax:**
```yaml
pipeline:
  - stage: intelligent_join
    args: [ "selectorPrompt or auto", "actionPrompt", limit ]
```

**Example:**
```yaml
pipeline:
  - stage: intelligent_join
    args: [ "auto", "click product link", 20 ]
```

---

### 3. IExtract

**Purpose**: LLM extraction on HTML block (chunking)

**YAML Syntax:**
```yaml
pipeline:
  - stage: iextract
    # extractor is optional; if omitted a default { selector: "body", method: "code" } is injected
    args: [ prompt, prefix ]
```

**Example:**
```yaml
pipeline:
  - stage: iextract
    args:
      - "Extract product specifications as title, price and sku"
      - "spec_"
```

---

### 4. Intelligent FlatSelect

**Purpose**: Segmentation + multi-row extraction with intelligent selector inference.

**Key behavior**:
- Accepts either a **literal CSS selector** (fast path) or a **natural language segmentation prompt**.
- Uses **template-aware selector caching** and **RoadRunner** (template recognition) to re-use inferred selectors across pages that share the same layout template.

**YAML Syntax:**
```yaml
pipeline:
  - stage: intelligent_flatSelect
    args: [ segPrompt, extrPrompt, prefix ]
```

**Example:**
```yaml
pipeline:
  - stage: intelligent_flatSelect
    args: [ "product cards", "extract name and price", "product" ]
```

---

## Plugin Stages (example-plugin)

All stages below are available only when the `example-plugin` is loaded and `Plugin.registerAll()` has been called.

### Browser / per-row fetch stages

#### `wget` (alias: `fetch`)

**Purpose**: Fetch a URL from a column using HTTP.

**Args**:
- `0` (optional): URL extractor (usually `$url`). Defaults to `_` (internal default column).

```yaml
pipeline:
  - stage: wget
    args: [ "$url" ]
```

#### `visit`

**Purpose**: Fetch a URL from a column using browser automation.

**Args**:
- `0` (optional): URL extractor (usually `$url`). Defaults to `_`.

```yaml
pipeline:
  - stage: visit
    args: [ "$url" ]
```

#### `visitJoin`

**Purpose**: Follow links using a browser (Visit) for each row.

**Args**:
- `0` (required): selector or `$column` containing URLs
- `1` (optional): joinType (`Inner` / `LeftOuter`, default `LeftOuter`)

```yaml
pipeline:
  - stage: visitJoin
    args: [ "a.product-link", "LeftOuter" ]
```

#### `visitExplore`

**Purpose**: Breadth-first crawling using a browser (Visit).

**Args**:
- `0` (required): selector or `$column` containing URLs
- `1` (optional): depth (Int, default `1`)

```yaml
pipeline:
  - stage: visitExplore
    args: [ "li.next a", 2 ]
```

---

### Extraction stages

#### `flatSelect` (alias: `widen`)

**Purpose**: Segment the page into repeated blocks and extract one output row per block.

**Args**:
- `0` (required): segment selector (String)
- `1` (optional): list of extractor maps applied inside each segment

```yaml
pipeline:
  - stage: flatSelect
    args:
      - "div.product"
      - - { selector: "h3", method: "text", as: "name" }
        # NOTE: for flatSelect the plugin stage expects `attr(name)` style
        - { selector: "img", method: "attr(src)", as: "img_src" }
```

#### `intelligent_table` (**placeholder/no-op**)

**Purpose**: Placeholder stage for LLM table extraction (currently does not perform extraction).

**Args**: none (current implementation does not use `args`).

```yaml
pipeline:
  - stage: intelligent_table
    args: []
```

#### `intelligentExtract`

**Purpose**: LLM-powered ad-hoc extraction from an HTML field (row transform).

**Args**:
- `0` (required): input field name containing HTML/text
- `1` (required): query/prompt
- `2` (required): output field name (result JSON string)

```yaml
pipeline:
  - stage: intelligentExtract
    args: [ "description_html", "Extract brand and model", "llm_json" ]
```

#### `iextract`

**Purpose**: LLM extraction that produces multiple columns (usually with a prefix).

**Args**:
- If the first argument is omitted or is not an extractor map / `$column`, a default extractor `{ selector: "body", method: "code" }` is injected.
- Then:
  - `prompt` (String)
  - `prefix` (optional String)

```yaml
pipeline:
  - stage: iextract
    args:
      - "Extract title as title and price as price and product code as sku"
      - "prod_"
```

---

### Utility + aggregation stages

#### `echo`

**Purpose**: Debug helper; writes `_echo` column.

**Args**:
- `0` (optional): message string

```yaml
pipeline:
  - stage: echo
    args: [ "hello" ]
```

#### `filter_country`

**Purpose**: Keep only rows whose `country` field is in the allowed list.

**Args**: one or more country codes.

```yaml
pipeline:
  - stage: filter_country
    args: [ "IT", "FR" ]
```

#### `sentiment`

**Purpose**: Simple lexicon-based sentiment on a text field; adds `sentiment` and `count`.

**Args**:
- `0` (optional): text field name (default: `message`)

```yaml
pipeline:
  - stage: sentiment
    args: [ "message" ]
```

#### `aggregatesentiment`

**Purpose**: Reduce-by-key aggregation; sums `sentiment` and `count` by key.

**Args**:
- `0` (optional): group field name (default: `entity`)

```yaml
pipeline:
  - stage: aggregatesentiment
    args: [ "country" ]
```

#### `avg_sentiment_by_key`

**Purpose**: Group-by-key and compute average sentiment into `avg_sentiment`.

**Args**:
- `0` (optional): group field name (default: `entity`)

```yaml
pipeline:
  - stage: avg_sentiment_by_key
    args: [ "country" ]
```

#### `sentiment_monthly`

**Purpose**: Macro-stage that runs `sentiment`, derives `month` from `date` (YYYY-MM-DD), then runs `aggregatesentiment` by month.

**Args**:
- `0` (optional): text field name (default: `message`)

```yaml
pipeline:
  - stage: sentiment_monthly
    args: [ "message" ]
```

#### `sum_sales`

**Purpose**: Reduce-by-key aggregation; sums numeric `sales` by `country`.

**Args**: none.

```yaml
pipeline:
  - stage: sum_sales
    args: []
```

---

### I/O stages (CSV + connectors)

#### `load_csv`

**Purpose**: Load a CSV into the pipeline (creates a new dataset).

**Args**:
- `0` (required): either a path string OR a map `{ path: "...", <spark_options...> }`
- `1..n` (optional): `key=value` Spark read options

```yaml
pipeline:
  - stage: load_csv
    args:
      - { path: "s3a://bucket/input.csv", header: "true", inferSchema: "true" }
```

#### `save_csv`

**Purpose**: Save current dataset as CSV (returns the same plan so you can continue).

**Args**:
- `0` (required): output path
- `1` (optional): mode (`overwrite|append|errorifexists|ignore`, default `overwrite`)

```yaml
pipeline:
  - stage: save_csv
    args: [ "s3a://bucket/out/", "overwrite" ]
```

#### Connector load stages

All connector stages accept as first argument either:
- a string (path / table / resource), or
- a map `{ path: "...", <options...> }` depending on the connector.

**Available stages**:
- `load_avro`
- `load_delta`
- `load_iceberg`
- `load_xml`
- `load_bigquery` (table or options with `table`)
- `load_athena` (JDBC options: `url`, `dbtable`, `driver`…)
- `load_mongodb` (options: `uri`, `database`, `collection`…)
- `load_cassandra` (`keyspace.table` or options with `keyspace` + `table`)
- `load_elasticsearch` (options with `es.resource`, `es.nodes`…)
- `load_kafka` (options with `kafka.bootstrap.servers`, `subscribe`…)

---

### External API fetch stages

#### `searchEngine` (alias: `search`)

**Purpose**: Search by EAN using a provider (Google Custom Search / Bing) and optionally enrich results.

**Args**:
- `0` (required): config map with keys like:
  - `provider`: `google` or `bing`
  - `ean`: literal EAN or `$ean_column`
  - `api_key`, `cx` (google), optional if provided via environment
  - `num_results`, `image_search`, `enrich`, `as`

```yaml
pipeline:
  - stage: searchEngine
    args:
      - provider: "google"
        ean: "$ean"
        num_results: 10
        image_search: true
        enrich: true
        as: "search_json"
```

#### `socialAPI` (alias: `social`)

**Purpose**: Fetch JSON from social/financial APIs (GET/POST) with auth via header or query param.

**Args**:
- `0` (required): config map with keys like `provider`, `endpoint`, `params`, `auth_token`, `method`, `body`, `as`

```yaml
pipeline:
  - stage: socialAPI
    args:
      - provider: "twitter"
        endpoint: "tweets/search/recent"
        params: { query: "python", max_results: 10 }
        auth_token: "${TWITTER_BEARER_TOKEN}"
        as: "tweets_json"
```

#### `eurostatAPI` (aliases: `eurostat`, `macroEU`)

**Purpose**: Fetch Eurostat REST API JSON.

**Args**:
- `0` (required): config map: `dataset`, optional `filters`, optional `params`, `as`

#### `istatAPI` (aliases: `istat`, `macroIT`)

**Purpose**: Fetch ISTAT SDMX JSON.

**Args**:
- `0` (required): config map: `flow`, optional `key`, optional `provider`, optional `params`, `as`

---

### Matching / scoring stages

#### `enrichMatchingScore`

**Purpose**: Recalculate matching score based on input fields and `iextract` output prefix.

**Args**:
- `0` (optional): config map (all keys optional; defaults are applied)

```yaml
pipeline:
  - stage: enrichMatchingScore
    args:
      - ean_field: "EAN number"
        description_field: "Item description"
        brand_field: "Brand"
        extracted_prefix: "prod_"
        output_field: "matching_score"
```

#### `imageSimilarity`

**Purpose**: Evaluate image similarity scores using LLM + heuristics. Expects image URLs in fields like `images` and `prod_product_image_urls`.

**Args**: none.

---

### Use-case stages (mostly placeholders)

These stages exist and are registered, but several are currently **no-op placeholders** (see code comments in `UseCaseStages.scala`).

#### `priceNormalize`

**Purpose**: normalize price strings into `price_numeric`, `price_currency`, and `price_<currency>`.

**Args**:
- `0` (optional): target currency (default `USD`)

#### `priceCompare` (**placeholder/no-op**)

**Args**: none.

#### `oddsNormalize`

**Purpose**: convert odds to `odds_decimal`.

**Args**: none.

#### `arbitrageDetect` (**placeholder/no-op**)

**Args**: none.

#### `propertyNormalize`

**Purpose**: compute `area_sqm` and `price_per_sqm`.

**Args**: none.

#### `realEstateArbitrage`

**Purpose**: compute simple z-score outliers (`arbitrage_z`, `is_arbitrage`) from `price_per_sqm`.

**Args**: none.

#### `trendAggregate` (**placeholder/no-op**)

**Args**: none.

#### `autoScroll` (**placeholder/no-op**)

**Args**:
- `0` (optional): max iterations (default `5`)
- `1` (optional): wait seconds (default `1.0`)

---

### Advanced analytics stages

All stages below accept a single optional config map as `args[0]`.

#### `propertyCluster` (KMeans / DBSCAN fallback)
#### `propertyClusterML` (KMeans / GMM)
#### `surebetFinder`
#### `fundamentalAnalysis`
#### `portfolioDataPrep`
#### `technicalIndicators`


## Attribute Resolvers

### Native Methods

Built-in extraction methods available in `extract` stages:

| Method | Description | Example |
|--------|-------------|---------|
| `text` | Extract visible text | `{ selector: "h1", method: "text", as: "title" }` |
| `code` | Extract full HTML | `{ selector: "div", method: "code", as: "html" }` |
| `html` | Alias of `code` (legacy) | `{ selector: "article", method: "html", as: "content" }` |
| `attr:NAME` | Extract HTML attribute (recommended for `extract`) | `{ selector: "a", method: "attr:href", as: "link" }` |
| `attrs` | Extract all attributes | `{ selector: "img", method: "attrs", as: "image_attrs" }` |

---

### Custom Attribute Resolvers

Custom resolvers are registered via plugins and can be used in YAML:

**Available Custom Resolvers:**

| Resolver | Description | Arguments | Example |
|----------|-------------|-----------|---------|
| `price` | Extract a numeric price token from text | none | `{ selector: "span.price", method: "price", as: "price_numeric" }` |
| `llm` | LLM-based extraction | optional instruction string (`args: [...]`) | `{ selector: "div", method: "llm", args: ["extract brand and model"], as: "llm_map" }` |

**Usage:**
```yaml
pipeline:
  - stage: extract
    args:
      - { selector: "span.price", method: "price", as: "price_numeric" }
      - { selector: "div.product", method: "llm", args: ["extract specifications"], as: "specs" }
```

**How Attribute Resolvers Work:**

1. **Resolution Chain**: When using an extraction method, the system checks:
   - First: Native methods (`text`, `code`, `attr(*)`)
   - Then: AttributeResolver Registry
   - Finally: Dynamic invocation if found

2. **Registration**: Custom resolvers are registered in `AttributeResolverRegistry` during plugin initialization

3. **Arguments**: Arguments are passed to the resolver in order via the `args` array

---

## Custom Actions (Traces)

### Action Factories

Built-in action factories for browser interactions:

| Action | Parameters | Example |
|--------|------------|---------|
| `visit` | `url` (String), optional `cooldown` (seconds) | `{ action: "visit", params: { url: "https://example.com", cooldown: 0.5 } }` |
| `wait` | `seconds` (Int/Double) | `{ action: "wait", params: { seconds: 2 } }` |
| `scroll_to_bottom` | `behavior` = `smooth\|auto` | `{ action: "scroll_to_bottom", params: { behavior: "smooth" } }` |
| `prompt` | `prompt` (String) or `text` (String) | `{ action: "prompt", params: { prompt: "click the login button" } }` |

**Usage:**
```yaml
fetch:
  url: "https://example.com"
  traces:
    - { action: "wait", params: { seconds: 1 } }
    - { action: "scroll_to_bottom", params: { behavior: "smooth" } }
    - { action: "prompt", params: { prompt: "click the login button" } }  # AI-driven action
```

### Custom Actions

Custom actions can be added via plugins by implementing an `ActionFactory` and making it discoverable by the runtime (ServiceLoader-based discovery).

**Usage in YAML:**
```yaml
fetch:
  url: "https://example.com"
  traces:
    - { action: "custom_click", params: { selector: ".button" } }
```

---

## Python Extensions

### Python Row Transform Stages

Python functions that transform entire rows:

**Function Signature:**
```python
def my_transform(row: Dict[str, Any]) -> Dict[str, Any]:
    """Transform row data"""
    if hasattr(row, 'asDict'):
        row_dict = row.asDict()
    else:
        row_dict = dict(row)
    
    # Your transformation logic
    return row_dict
```

**Registration:**
```python
python_registry.register_row_transform("my_transform", my_transform)
```

**Usage in YAML:**
```yaml
pipeline:
  - stage: python_row_transform:my_transform
```

---

### Runtime requirement

Python row transforms require the Spark job runner to register the Python registry via Py4J (`PythonBridgeRegistry.setPythonRegistry(...)`). If a function name is not registered, the corresponding `python_row_transform:<name>` stage will fail at runtime.

### Inline `python_extensions` (for API code-generation)

Some API flows support providing `python_extensions` alongside the pipeline YAML. The Scala YAML parser ignores this section, but the API can use it to generate PySpark code that registers these functions.

```yaml
python_extensions:
  stages:
    my_transform:
      type: row_transform
      function: |
        def my_transform(row):
            row["processed"] = True
            return row
```

---

## Complete Example

```yaml
fetch:
  url: "https://shop.example.com"
  traces:
    - { action: "wait", params: { seconds: 1 } }
    - { action: "prompt", params: { prompt: "accept cookies if present" } }

pipeline:
  # Intelligent exploration
  - stage: intelligent_explore
    args: [ "category links", 2 ]
  
  # Join product pages (LLM-assisted selector + optional inferred actions + optional limit)
  - stage: intelligent_join
    args: [ "product detail links", "none", 20 ]
  
  # Extract with native and custom resolvers
  - stage: extract
    args:
      - { selector: "h1.title", method: "text", as: "product_title" }
      - { selector: "span.price", method: "price", as: "price_numeric" }
      - { selector: "div.description", method: "code", as: "description_html" }
      - { selector: "img.product-image", method: "attr:src", as: "image_url" }
      - { selector: "div.reviews", method: "llm", args: ["Extract average rating"], as: "rating" }
  
  # Python transformation
  - stage: python_row_transform:normalize_price
    args: []
  
  # Filter by country
  - stage: filter_country
    args: [ "US" ]
```

---

## Best Practices

1. **Start Simple**: Begin with native methods (`text`, `code`, `attr`)
2. **Use Custom Resolvers**: Only for complex, reusable extraction logic
3. **Prefer Wget**: Use `wget` for static content, `visit` only when JavaScript is needed
4. **AI Traces**: Use AI-driven traces for adaptive scraping resilient to layout changes
5. **Python Extensions**: Use Python extensions for complex data transformations
6. **Error Handling**: Always handle edge cases in custom resolvers and Python functions
7. **Documentation**: Document custom resolvers and Python functions with clear docstrings

---

## API Integration

### Store pipeline YAML (Agent)

```bash
curl -X POST https://api.webrobot.eu/api/webrobot/api/agents \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-agent",
    "categoryId": "1",
    "pipelineYaml": "pipeline:\n  - stage: join\n    args: [\"a.product-link\", \"LeftOuter\"]\n  - stage: extract\n    args:\n      - { selector: \"h1\", method: \"text\", as: \"title\" }",
    "enabled": true
  }'
```

### Update pipeline YAML (Agent)

```bash
curl -X PUT https://api.webrobot.eu/api/webrobot/api/agents/1/123 \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "pipelineYaml": "pipeline:\n  - stage: join\n    args: [\"a.product-link\"]\n  - stage: extract\n    args:\n      - { selector: \"h1\", method: \"text\", as: \"title\" }"
  }'
```

---

## Next Steps

- Learn how to [build a complete pipeline](build-a-pipeline.md)
- Explore [Attribute Resolvers](build-a-pipeline.md#attribute-resolvers) in detail
- Check out [Python Extensions](build-a-pipeline.md#python-extensions) guide
- If you are using the EAN plugin, see [EAN Image Sourcing Plugin](ean-image-sourcing.md) for the stage set + CloudCredential injection behavior.
- Review the [API Reference](../openapi.yaml) for complete endpoint documentation
