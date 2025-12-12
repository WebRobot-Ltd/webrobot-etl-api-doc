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
- `selector` (String): CSS selector or prompt for link discovery
- `depth` (Int): Maximum depth to crawl
- `trace` (Optional): Browser interaction trace

**Example:**
```yaml
pipeline:
  - stage: explore
    args: [ "a.category", 3 ]
```

---

### 2. Join

**Purpose**: Visit N child links for each row

**YAML Syntax:**
```yaml
pipeline:
  - stage: join
    args: [ "a.product-link", "none", 20 ]  # selector, action, limit
```

**Arguments:**
- `selector` (String): CSS selector for links to visit
- `action` (String): Action prompt (`"none"` if no action needed)
- `limit` (Int): Maximum number of links to visit per row

**Example:**
```yaml
pipeline:
  - stage: join
    args: [ "a.detail-link", "none", 10 ]
```

---

### 3. Extract

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
  args: [ "USD" ]               # Optional: method arguments
  as: "price_usd"              # Optional: output column alias
```

**Example:**
```yaml
pipeline:
  - stage: extract
    args:
      - { selector: "h1", method: "text", as: "title" }
      - { selector: "span.price", method: "price", args: ["USD"], as: "price_usd" }
      - { selector: "a", method: "attr(href)", as: "link" }
```

---

### 4. FlatSelect

**Purpose**: Segment HTML block and create one row per segment

**YAML Syntax:**
```yaml
pipeline:
  - stage: flatSelect
    args: [ "div.product", "extraction_prompt_or_selector_map", "prefix" ]
```

**Arguments:**
- `selector` (String): CSS selector for segmentation
- `extraction` (String/List): Extraction prompt or selector-map list
- `prefix` (String): Prefix for output columns

**Example:**
```yaml
pipeline:
  - stage: flatSelect
    args:
      - "div.product-item"
      - "Extract product name and price"
      - "product"
```

---

## Intelligent Stages (LLM-powered)

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
    args: [ extractor, prompt, prefix ]
```

**Example:**
```yaml
pipeline:
  - stage: iextract
    args: [ "div.content", "Extract product specifications", "spec" ]
```

---

### 4. Intelligent FlatSelect

**Purpose**: Segmentation + LLM multiple extraction

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

## Utility Stages

### Echo

**Purpose**: Copy row (debug utility)

```yaml
pipeline:
  - stage: echo
```

---

### Filter Country

**Purpose**: Filter rows by country

```yaml
pipeline:
  - stage: filter_country
    args: [ "US" ]  # country code
```

---

### Sentiment

**Purpose**: Calculate sentiment for single row

```yaml
pipeline:
  - stage: sentiment
    args: [ "text_column" ]  # column name
```

---

### Intelligent Table

**Purpose**: LLM table parsing

```yaml
pipeline:
  - stage: intelligent_table
    args: [ "table selector", "extraction prompt" ]
```

---

## Use-Case Stages

### E-commerce

| Stage | Purpose |
|-------|---------|
| `priceNormalize` | Normalize price formats |
| `priceCompare` | Compare prices across sources |

**Example:**
```yaml
pipeline:
  - stage: priceNormalize
    args: []
  - stage: priceCompare
    args: []
```

---

### Real Estate

| Stage | Purpose |
|-------|---------|
| `propertyNormalize` | Normalize property data |
| `realEstateArbitrage` | Detect arbitrage opportunities |

---

### Bookmaker

| Stage | Purpose |
|-------|---------|
| `oddsNormalize` | Normalize odds formats |
| `arbitrageDetect` | Detect arbitrage opportunities |

---

## Attribute Resolvers

### Native Methods

Built-in extraction methods available in `extract` stages:

| Method | Description | Example |
|--------|-------------|---------|
| `text` | Extract visible text | `{ selector: "h1", method: "text", as: "title" }` |
| `code` | Extract full HTML | `{ selector: "div", method: "code", as: "html" }` |
| `html` | Alias of `code` (legacy) | `{ selector: "article", method: "html", as: "content" }` |
| `attr(name)` | Extract HTML attribute | `{ selector: "a", method: "attr(href)", as: "link" }` |
| `attrs` | Extract all attributes | `{ selector: "img", method: "attrs", as: "image_attrs" }` |

---

### Custom Attribute Resolvers

Custom resolvers are registered via plugins and can be used in YAML:

**Available Custom Resolvers:**

| Resolver | Description | Arguments | Example |
|----------|-------------|-----------|---------|
| `price` | Extract and normalize price | 0-1 ⇒ targetCurrency | `{ selector: "span.price", method: "price", args: ["USD"], as: "price_usd" }` |
| `llm` | LLM-based extraction | prompt (String), optional prefix | `{ selector: "div", method: "llm", args: ["Extract dimensions"], as: "data" }` |
| `sentiment` | Sentiment analysis | text | `{ selector: "p.review", method: "sentiment", as: "sentiment" }` |

**Usage:**
```yaml
pipeline:
  - stage: extract
    args:
      - { selector: "span.price", method: "price", args: ["USD"], as: "price_usd" }
      - { selector: "div.product", method: "llm", args: ["Extract specifications"], as: "specs" }
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
| `wait` | `seconds` (Int/Double) | `{ action: "wait", params: { seconds: 2 } }` |
| `scroll_to_bottom` | `behavior` = `smooth\|auto` | `{ action: "scroll_to_bottom", params: { behavior: "smooth" } }` |

**Usage:**
```yaml
fetch:
  url: "https://example.com"
  traces:
    - { action: "wait", params: { seconds: 1 } }
    - { action: "scroll_to_bottom", params: { behavior: "smooth" } }
    - { prompt: "click the login button" }  # AI-driven action
```

### Custom Actions

Custom actions can be registered via plugins:

**Registration:**
```scala
// In plugin initialization
ActionFactoryRegistry.register("custom_click", CustomClickFactory)
```

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
    name: "Transform data"
```

---

### Python Attribute Resolvers

Python functions that resolve specific attributes:

**Function Signature:**
```python
def my_resolver(elem: Any, attribute_name: Optional[str] = None) -> Any:
    """Resolve attribute value"""
    if not elem:
        return None
    # Your resolution logic
    return resolved_value
```

**Registration:**
```python
python_registry.register_attribute_resolver("my_resolver", my_resolver)
```

**Usage in YAML:**
```yaml
pipeline:
  - stage: extract
    args:
      - { selector: "div.data", method: "python_resolver:my_resolver", as: "resolved_value" }
```

---

### Python Intelligent Actions

Python functions for intelligent browser actions:

**Function Signature:**
```python
def my_action(page: Any, params: Dict[str, Any]) -> bool:
    """Execute custom browser action"""
    # Your action logic
    return True
```

**Registration:**
```python
python_registry.register_action("my_action", my_action)
```

**Usage in YAML:**
```yaml
fetch:
  url: "https://example.com"
  traces:
    - { action: "python_action:my_action", params: { key: "value" } }
```

---

## Conditional Execution

Stages can be conditionally executed using `when` clauses:

```yaml
pipeline:
  - stage: extract
    when:
      condition: "env.LIMIT > 100"
    args:
      - { selector: "h1", method: "text", as: "title" }
```

**Supported Conditions:**
- Environment variables: `env.VAR_NAME == 'value'`
- Parameters: `params.PARAM_NAME == 'value'`
- Logical operators: `&&`, `||`, `!`

---

## Complete Example

```yaml
fetch:
  url: "https://shop.example.com"
  traces:
    - { action: "wait", params: { seconds: 1 } }
    - { prompt: "accept cookies if present" }

globals:
  limit_pages: 50

pipeline:
  # Intelligent exploration
  - stage: intelligent_explore
    args: [ "category links", 2 ]
  
  # Join product pages
  - stage: join
    args: [ "a.product-link", "none", 20 ]
  
  # Extract with native and custom resolvers
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

### Create Pipeline with YAML

```bash
curl -X POST https://api.webrobot.eu/api/webrobot/api/pipelines \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "your-project-id",
    "name": "my-pipeline",
    "yamlContent": "pipeline:\n  - stage: extract\n    args:\n      - { selector: \"h1\", method: \"text\", as: \"title\" }",
    "enabled": true
  }'
```

### Update Pipeline YAML

```bash
curl -X PUT https://api.webrobot.eu/api/webrobot/api/pipelines/1 \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "yamlContent": "pipeline:\n  - stage: extract\n    args:\n      - { selector: \"h1\", method: \"text\", as: \"title\" }"
  }'
```

---

## Next Steps

- Learn how to [build a complete pipeline](build-a-pipeline.md)
- Explore [Attribute Resolvers](build-a-pipeline.md#attribute-resolvers) in detail
- Check out [Python Extensions](build-a-pipeline.md#python-extensions) guide
- Review the [API Reference](../openapi.yaml) for complete endpoint documentation
