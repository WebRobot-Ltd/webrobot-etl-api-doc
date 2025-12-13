---
title: Pipeline Examples
version: 1.0.0
description: Copy-pasteable YAML pipeline examples aligned with the current parser and stages
---

# Pipeline Examples

These examples are **real YAML files** in the repository under `examples/pipelines/`. They are designed to match the current YAML parser expectations:
- Top-level `pipeline` must be a list of `{ stage, args }`
- Each stage entry must contain only `stage` and `args` (no extra keys)
- `fetch.traces` items must use `action`/`factory` + optional `params`

## Static crawl (HTTP only)

- File: `examples/pipelines/01-static-books.yaml`

```yaml
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
      - { selector: ".product_main img", method: "attr:src", as: "image_src" }
```

## Dynamic crawl (browser + flatSelect)

- File: `examples/pipelines/02-dynamic-quotes.yaml`

```yaml
fetch:
  url: "https://quotes.toscrape.com"
  traces:
    - { action: "visit", params: { url: "https://quotes.toscrape.com", cooldown: 0.5 } }
    - { action: "wait", params: { seconds: 1 } }

pipeline:
  - stage: visitJoin
    args: [ "a.tag", "LeftOuter" ]
  - stage: flatSelect
    args:
      - "div.quote"
      - - { selector: "span.text", method: "text", as: "quote_text" }
        - { selector: "small.author", method: "text", as: "author" }
```

## LLM extraction (`iextract`) with prompt-only args

- File: `examples/pipelines/03-iextract-prompt-only.yaml`

```yaml
fetch:
  url: "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

pipeline:
  - stage: iextract
    args:
      - "Extract title as title and price as price and product code as sku"
      - "prod_"
```

## Attribute resolvers (column-based + selector-based)

- File: `examples/pipelines/04-attribute-resolvers.yaml`

```yaml
fetch:
  url: "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

pipeline:
  - stage: extract
    args:
      - { selector: "h1", method: "text", as: "title" }
      - { selector: ".price_color", method: "text", as: "price_raw" }
      - { selector: "#content_inner article", method: "text", as: "description_text" }
      - { field: "price_raw", method: "price", as: "price_numeric" }
      - { field: "description_text", method: "llm", as: "llm_features" }
      - { field: "description_text", method: "llm", args: ["extract 3 bullet points of benefits"], as: "llm_map" }
```

## Python row transforms (`python_row_transform:<name>`)

- File: `examples/pipelines/05-python-row-transforms.yaml`

```yaml
python_extensions:
  stages:
    price_normalizer:
      type: row_transform
      function: |
        def price_normalizer(row):
            # ... your python code ...
            return row

fetch:
  url: "https://books.toscrape.com"

pipeline:
  - stage: extract
    args:
      - { selector: ".product_pod h3 a", method: "text", as: "title" }
      - { selector: ".product_pod .price_color", method: "text", as: "price_raw" }
  - stage: python_row_transform:price_normalizer
    args: []
```


