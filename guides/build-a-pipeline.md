---
title: Build a Pipeline
version: 1.0.0
description: Guide to building ETL pipelines using YAML syntax and the WebRobot ETL API
---

# Build a Pipeline

This guide explains how to create ETL pipelines using YAML syntax and the WebRobot ETL API. You'll learn how to structure pipeline YAML files, define stages, use attribute resolvers, and extend pipelines with custom actions and Python extensions.

## Overview

A pipeline YAML file defines:
- **Fetch Configuration**: Initial URL and browser traces
- **Pipeline Stages**: Sequential data processing steps
- **Attribute Resolvers**: Custom extraction methods
- **Custom Actions**: Browser interaction extensions
- **Python Extensions**: Custom Python stages and resolvers

## Pipeline YAML Structure

### Basic Structure

```yaml
fetch:          # Optional - initial page fetch
  url: "https://example.com"
  traces:       # Optional - browser interactions
    - { action: "wait", params: { seconds: 2 } }
    - { prompt: "click the accept cookies button" }

globals:        # Optional - global variables
  limit_pages: 50
  site_url: "https://example.com"

pipeline:       # REQUIRED - ordered list of stages
  - stage: explore
    args: [ "a.category", 1 ]
  - stage: extract
    args:
      - { selector: "h1", method: "text", as: "title" }
```

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
| `explore` | Breadth-first link discovery | selector/prompt, depth (Int), optional trace |
| `join` | Visit N child links per row | selector, action prompt (`"none"` if absent), limit (Int) |
| `extract` | Extract fields using selector-map | List of selector-map objects |
| `flatSelect` | Segment HTML block, create row per segment | selector, extraction prompt or selector-map list, prefix |

### Intelligent Stages (LLM-powered)

| Stage | Description | Arguments |
|-------|-------------|-----------|
| `intelligent_explore` | Like `explore`, but uses LLM to infer selector from NL prompt | prompt, depth, optional trace |
| `intelligent_join` | Join with inferred selector (PTA/LLM) + inferred actions | selectorPrompt or `"auto"`, actionPrompt, limit |
| `iextract` | LLM extraction on HTML block (chunking) | extractor, prompt, prefix |
| `intelligent_flatSelect` | Segmentation + LLM multiple extraction | segPrompt, extrPrompt, prefix |

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
      - { selector: "a", method: "attr(href)", as: "link" }
      
      # Extract all attributes
      - { selector: "img", method: "attrs", as: "image_attrs" }
```

### Custom Attribute Resolvers

Custom resolvers are registered via plugins and can be used in YAML:

```yaml
pipeline:
  - stage: extract
    args:
      # Custom price resolver
      - { selector: "span.price", method: "price", args: ["USD"], as: "price_usd" }
      
      # Custom LLM resolver
      - { selector: "div.product", method: "llm", args: ["Extract dimensions and weight"], as: "llm_extracted" }
      
      # Custom sentiment resolver
      - { selector: "p.review", method: "sentiment", as: "review_sentiment" }
```

**Available Custom Resolvers:**

| Resolver | Description | Arguments |
|----------|-------------|-----------|
| `price` | Extract and normalize price | 0-1 ⇒ targetCurrency (e.g., `"USD"`) |
| `llm` | LLM-based extraction | prompt (String), optional prefix |
| `sentiment` | Sentiment analysis | text |

## Step 4: Custom Actions (Traces)

### Action Factories

Built-in action factories for browser interactions:

```yaml
fetch:
  url: "https://example.com"
  traces:
    # Wait action
    - { action: "wait", params: { seconds: 2 } }
    
    # Scroll action
    - { action: "scroll_to_bottom", params: { behavior: "smooth" } }
    
    # AI-driven action (requires TOGETHER_AI_API_KEY)
    - { prompt: "click the login button" }
    - { prompt: "fill the search form with 'laptop'" }
```

**Available Actions:**

| Action | Parameters |
|--------|------------|
| `wait` | `seconds` (Int/Double) |
| `scroll_to_bottom` | `behavior` = `smooth|auto` |

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
    name: "Transform data"
```

### Python Attribute Resolvers

Python functions that resolve specific attributes:

```python
def my_resolver(elem: Any, attribute_name: Optional[str] = None) -> Any:
    """Resolve attribute value"""
    if not elem:
        return None
    # Your resolution logic
    return resolved_value
```

**Usage in YAML:**

```yaml
pipeline:
  - stage: extract
    args:
      - { selector: "div.data", method: "python_resolver:my_resolver", as: "resolved_value" }
```

### Python Intelligent Actions

Python functions for intelligent browser actions:

```python
def my_action(page: Any, params: Dict[str, Any]) -> bool:
    """Execute custom browser action"""
    # Your action logic
    return True
```

**Usage in YAML:**

```yaml
fetch:
  url: "https://example.com"
  traces:
    - { action: "python_action:my_action", params: { key: "value" } }
```

## Step 6: Complete Pipeline Example

### E-commerce Product Scraper

```yaml
fetch:
  url: "https://shop.example.com"
  traces:
    - { action: "wait", params: { seconds: 1 } }
    - { prompt: "accept cookies if present" }

pipeline:
  # Intelligent exploration
  - stage: intelligent_explore
    args: [ "category links", 2 ]
  
  # Join product pages
  - stage: join
    args: [ "a.product-link", "none", 20 ]
  
  # Extract product data
  - stage: extract
    args:
      - { selector: "h1.title", method: "text", as: "product_title" }
      - { selector: "span.price", method: "price", args: ["USD"], as: "price_usd" }
      - { selector: "div.description", method: "code", as: "description_html" }
      - { selector: "img.product-image", method: "attr(src)", as: "image_url" }
      - { selector: "div.reviews", method: "llm", args: ["Extract average rating"], as: "rating" }
  
  # Python transformation
  - stage: python_row_transform:normalize_price
    name: "Normalize prices"
  
  # Price comparison
  - stage: priceCompare
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
