---
title: Build a Pipeline
version: 1.0.0
description: Guide to building ETL pipelines using YAML syntax and the WebRobot ETL API
---

# Build a Pipeline

This guide explains how to create ETL pipelines using YAML syntax and the WebRobot ETL API. It is aligned with the current **Scala YAML parser + stage implementations** shipped in the `webrobot-etl` core and `example-plugin`.

## Overview

A pipeline YAML file defines:
- **Fetch configuration**: initial URL and optional `traces` (browser actions)
- **Pipeline stages**: sequential processing steps
- **Attribute resolvers**: custom extraction methods usable in `extract`/`flatSelect`
- **Custom actions (factories)**: reusable actions usable in `fetch.traces`
- **Python extensions**: custom Python row transforms usable as stages (`python_row_transform:<name>`)

## Pipeline YAML Structure

### Basic Structure

```yaml
fetch:          # Optional - initial page fetch
  url: "https://example.com"
  traces:       # Optional - pre-actions (ActionFactory)
    - { action: "visit", params: { url: "https://example.com", cooldown: 0.5 } }
    - { action: "wait", params: { seconds: 2 } }
    - { action: "scroll_to_bottom", params: { behavior: "auto" } }
    - { action: "prompt", params: { prompt: "click the accept cookies button" } }

pipeline:       # REQUIRED - ordered list of stages
  - stage: explore
    args: [ "a.category", 1 ]
  - stage: extract
    args:
      - { selector: "h1", method: "text", as: "title" }
```

### What the engine actually reads

The execution engine reads:
- `fetch` (optional)
- `pipeline` (required)

Any extra top-level keys are ignored by the Scala parser (for example metadata, comments, or `python_extensions` used by higher-level tooling).

## Step 1: Create a Pipeline via API

First, create a pipeline configuration using the API:

```bash
curl -X POST https://api.webrobot.eu/api/webrobot/api/pipelines \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "your-project-id",
    "name": "my-pipeline",
    "description": "E-commerce product scraper",
    "yamlContent": "fetch:\n  url: \"https://shop.example.com\"\npipeline:\n  - stage: extract\n    args:\n      - { selector: \"h1\", method: \"text\", as: \"title\" }",
    "enabled": true
  }'
```

**Response:**
```json
{
  "id": 1,
  "projectId": "your-project-id",
  "name": "my-pipeline",
  "description": "E-commerce product scraper",
  "yamlContent": "...",
  "enabled": true,
  "createdAt": "2025-12-12T10:00:00Z"
}
```

## Step 2: Understanding Stage Types

### Core Stages

| Stage | Description | Arguments |
|-------|-------------|-----------|
| `join` | Follow links with HTTP (wget) | link selector (String or `$col`), optional joinType (`Inner`/`LeftOuter`) |
| `explore` | Crawl links breadth-first with HTTP (wget) | link selector (String or `$col`), optional depth (Int, default 1) |
| `visitJoin` | Follow links with a browser (Visit) | link selector (String or `$col`), optional joinType (`Inner`/`LeftOuter`) |
| `visitExplore` | Crawl links breadth-first with a browser (Visit) | link selector (String or `$col`), optional depth (Int, default 1) |
| `extract` | Extract fields (adds columns) | list of extractor definitions (maps or shorthands) |
| `flatSelect` (alias `widen`) | Segment into repeated blocks and extract one row per block | segment selector (String), list of extractor maps |
| `wget` (alias `fetch`) | Fetch a URL from a column using HTTP | optional extractor (usually `$url`, default `_`) |
| `visit` | Fetch a URL from a column using browser automation | optional extractor (usually `$url`, default `_`) |

### Intelligent Stages (LLM-powered)

| Stage | Description | Arguments |
|-------|-------------|-----------|
| `intelligentJoin` (alias `intelligent_join`) | Join with inferred selector + optional inferred actions | selectorPrompt (or `"auto"`), optional actionPrompt, optional limit (Int) |
| `intelligentExplore` (alias `intelligent_explore`) | Explore using an NL prompt (link inference) | prompt, optional depth (Int, default 1) |
| `iextract` | LLM extraction producing dynamic columns | html extractor (optional), prompt (String), prefix (optional) |

### Utility Stages

| Stage | Description |
|-------|-------------|
| `echo` | Copy row (debug) |
| `filter_country` | Filter rows by country |
| `sentiment` | Calculate sentiment for single row |
| `sentiment_monthly` | Aggregate sentiment by month |
| `intelligent_table` | LLM table parsing |

## Step 3: Using Attribute Resolvers

### Native Methods

Built-in extraction methods available in `extract` stages:

```yaml
pipeline:
  - stage: extract
    args:
      # Extract visible text
      - { selector: "h1", method: "text", as: "title" }
      
      # Extract full HTML
      - { selector: "div.content", method: "code", as: "html_content" }
      
      # Extract HTML attribute
      - { selector: "a", method: "attr:href", as: "link" }
      
      # Extract all attributes
      - { selector: "img", method: "attrs", as: "image_attrs" }
```

### Custom Attribute Resolvers

Custom resolvers are registered via plugins and can be used in YAML:

```yaml
pipeline:
  - stage: extract
    args:
      # PriceResolver (example-plugin): extracts the first numeric token from text
      - { selector: "span.price", method: "price", as: "price_numeric" }
      
      # LLMResolver (example-plugin): structured features
      - { selector: "div.description", method: "llm", as: "llm_features" }
      
      # LLMResolver with instruction (dynamic Map output)
      - { selector: "div.description", method: "llm", args: ["extract brand, model, and color"], as: "llm_map" }

      # Use a previously extracted field as input of a resolver (column-based)
      - { field: "description_text", method: "llm", args: ["extract sku and main benefits"], as: "llm_analysis" }
```

**Available Custom Resolvers:**

| Resolver | Description | Arguments |
|----------|-------------|-----------|
| `price` | Extract a numeric price token from text | none |
| `llm` | LLM-based extraction (structured features or custom key-value map) | optional instruction string (`args: [...]`) |

## Step 4: Custom Actions (Traces)

### Action Factories

Built-in action factories for browser interactions:

```yaml
fetch:
  url: "https://example.com"
  traces:
    # Visit (browser)
    - { action: "visit", params: { url: "https://shop.example.com", cooldown: 0.5 } }

    # Wait action
    - { action: "wait", params: { seconds: 2 } }
    
    # Scroll action
    - { action: "scroll_to_bottom", params: { behavior: "smooth" } }
    
    # AI-driven action (requires TOGETHER_AI_API_KEY)
    - { action: "prompt", params: { prompt: "click the login button" } }
    - { action: "prompt", params: { prompt: "fill the search form with 'laptop'" } }
```

**Available Actions:**

| Action | Parameters |
|--------|------------|
| `visit` | `url` (String), optional `cooldown` (seconds) |
| `wait` | `seconds` (Int/Double) |
| `scroll_to_bottom` | `behavior` = `smooth|auto` |
| `prompt` | `prompt` (String) or `text` (String) |

### Custom Actions

Custom actions can be registered via plugins and used in traces:

```yaml
fetch:
  url: "https://example.com"
  traces:
    - { action: "custom_click", params: { selector: ".button" } }
    - { action: "custom_fill", params: { selector: "#input", value: "text" } }
```

## Step 5: Python Extensions

### Python Row Transform Stages

Python functions that transform entire rows:

```python
def my_transform(row: Dict[str, Any]) -> Dict[str, Any]:
    """Transform row data"""
    if hasattr(row, 'asDict'):
        row_dict = row.asDict()
    else:
        row_dict = dict(row)
    
    # Your transformation logic
    row_dict['processed'] = True
    return row_dict
```

**Usage in YAML:**

```yaml
pipeline:
  - stage: python_row_transform:my_transform
```

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

## Step 6: Complete Pipeline Example

### E-commerce Product Scraper

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
  
  # Extract product data
  - stage: extract
    args:
      - { selector: "h1.title", method: "text", as: "product_title" }
      - { selector: "span.price", method: "price", as: "price_numeric" }
      - { selector: "div.description", method: "code", as: "description_html" }
      - { selector: "img.product-image", method: "attr:src", as: "image_url" }
      - { selector: "div.reviews", method: "llm", args: ["extract average rating"], as: "rating" }
  
  # Python transformation
  - stage: python_row_transform:normalize_price
    args: []
```

## Step 7: Update Pipeline YAML via API

Update the pipeline YAML content:

```bash
curl -X PUT https://api.webrobot.eu/api/webrobot/api/pipelines/1 \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "yamlContent": "fetch:\n  url: \"https://new-url.com\"\npipeline:\n  - stage: extract\n    args:\n      - { selector: \"h1\", method: \"text\", as: \"title\" }"
  }'
```

## Step 8: Execute Pipeline

Execute the pipeline:

```bash
curl -X POST https://api.webrobot.eu/api/webrobot/api/pipelines/1/execute \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "limit": 100
    }
  }'
```

## Python Example

Complete Python example for creating and executing pipelines:

```python
import requests

API_BASE = "https://api.webrobot.eu/api"
API_KEY = "your-api-key"
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Pipeline YAML content
pipeline_yaml = """
fetch:
  url: "https://shop.example.com"
  traces:
    - { action: "wait", params: { seconds: 1 } }

pipeline:
  - stage: intelligent_explore
    args: [ "category links", 1 ]
  
  - stage: extract
    args:
      - { selector: "h1", method: "text", as: "title" }
      - { selector: "span.price", method: "price", args: ["USD"], as: "price" }
"""

# Create pipeline
pipeline_data = {
    "projectId": "your-project-id",
    "name": "product-scraper",
    "description": "E-commerce product scraper",
    "yamlContent": pipeline_yaml,
    "enabled": True
}

response = requests.post(
    f"{API_BASE}/webrobot/api/pipelines",
    headers=HEADERS,
    json=pipeline_data
)
pipeline = response.json()
pipeline_id = pipeline["id"]

# Execute pipeline
response = requests.post(
    f"{API_BASE}/webrobot/api/pipelines/{pipeline_id}/execute",
    headers=HEADERS,
    json={"parameters": {"limit": 50}}
)
execution = response.json()
print(f"Execution ID: {execution['id']}")
```

## Next Steps

- Learn about [available pipeline stages](pipeline-stages.md)
- Explore [Attribute Resolvers](pipeline-stages.md#attribute-resolvers) in detail
- Check out [Python Extensions](pipeline-stages.md#python-extensions) guide
- Review the [API Reference](../openapi.yaml) for complete endpoint documentation
