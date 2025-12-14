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

- File: [`examples/pipelines/01-static-books.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/01-static-books.yaml)

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

- File: [`examples/pipelines/02-dynamic-quotes.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/02-dynamic-quotes.yaml)

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

- File: [`examples/pipelines/03-iextract-prompt-only.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/03-iextract-prompt-only.yaml)

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

- File: [`examples/pipelines/04-attribute-resolvers.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/04-attribute-resolvers.yaml)

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

- File: [`examples/pipelines/05-python-row-transforms.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/05-python-row-transforms.yaml)

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

## I/O operations (CSV load/save)

- File: [`examples/pipelines/06-io-load-save-csv.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/06-io-load-save-csv.yaml)

## Search engine integration (EAN enrichment)

- File: [`examples/pipelines/07-searchengine-ean-enrich.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/07-searchengine-ean-enrich.yaml)

## Browser automation (fetch.traces with actions)

- File: [`examples/pipelines/08-fetch-traces-browser-actions.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/08-fetch-traces-browser-actions.yaml)

## Multi-source aggregation (set union + dedup) — vertical-ready

These examples are meant to “prepare the ground” for verticals where you aggregate records from **multiple sources**.
The key idea is:
- **Union** records coming from different upstream crawls / sources (even if schemas differ).
- Apply **set semantics** via **dedup** using a stable key (e.g. `sku`, `ean`, `url`, plus `source`).

### 1) Union seed lists, dedup by URL, then fetch + extract

- File: [`examples/pipelines/09-multi-source-seeds-union-dedup.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/09-multi-source-seeds-union-dedup.yaml)

### 2) Stitch outputs from multiple crawls, then dedup by business key

- File: [`examples/pipelines/10-multi-source-results-union-dedup.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/10-multi-source-results-union-dedup.yaml)

### 3) Vertical pattern: run 2 source pipelines, then stitch their outputs

**Current approach (workaround)**: Since YAML pipelines are sequential and don't support branching, the pattern is:
- Run source pipeline A → save output to disk
- Run source pipeline B → save output to disk
- Run stitching pipeline → `load_union` + `dedup`

Files:
- Source A: [`examples/pipelines/11-vertical-source-a-offers.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/11-vertical-source-a-offers.yaml)
- Source B: [`examples/pipelines/12-vertical-source-b-offers.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/12-vertical-source-b-offers.yaml)
- Stitching: [`examples/pipelines/13-vertical-stitch-union-dedup-offers.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/13-vertical-stitch-union-dedup-offers.yaml)

**Single-pipeline (now supported via store/reset/union_with)**:

To avoid intermediate disk I/O, you can branch in-memory and merge within the same pipeline using helper stages:

- **Option A (single pipeline with in-memory branches)**: [`examples/pipelines/17-single-pipeline-multi-source-union.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/17-single-pipeline-multi-source-union.yaml)
  - `cache` (optional but recommended) before `store` to avoid recompute when reusing the branch
  - `store` caches the current dataset under a label
  - `reset` starts a fresh dataset
  - `union_with` unions the current dataset with a stored branch

- **Option B (same helpers, alternative flow)**: [`examples/pipelines/18-single-pipeline-alternative-syntax.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/18-single-pipeline-alternative-syntax.yaml)

## Vertical use cases

### Price comparison (5 e-commerce sites)

- File: [`examples/pipelines/19-price-comparison-5-sites.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/19-price-comparison-5-sites.yaml)

Aggregates product offers from Amazon, eBay, Walmart, Target, and Best Buy, with product matching by EAN.

### Sports betting odds aggregation (5 bookmakers)

- File: [`examples/pipelines/20-sports-betting-5-bookmakers.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/20-sports-betting-5-bookmakers.yaml)

Aggregates odds from bet365, Pinnacle, Betfair, William Hill, and Unibet for odds comparison.

### Surebet detection (intelligent extraction)

- File: [`examples/pipelines/21-surebet-intelligent-extraction.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/21-surebet-intelligent-extraction.yaml)

Uses `intelligent_explore` and `intelligent_flatSelect` to extract odds from bookmaker sites with complex, non-trivial table structures, then detects arbitrage (surebet) opportunities.

### Real estate arbitrage (property clustering)

- File: [`examples/pipelines/22-real-estate-arbitrage-clustering.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/22-real-estate-arbitrage-clustering.yaml)

Aggregates property listings from 5 real estate sites, clusters similar properties to identify the same property across sources, and detects arbitrage opportunities using external statistical sources (market averages, price percentiles).

### LLM fine-tuning dataset construction

- File: [`examples/pipelines/23-llm-finetuning-dataset.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/23-llm-finetuning-dataset.yaml)

Aggregates Q&A data from multiple sources (Stack Overflow, Reddit, documentation sites, GitHub issues, Wikipedia), cleans and normalizes text, converts to instruction-following format (Alpaca style), and exports to JSONL for LLM fine-tuning.

Note: Paths can use environment placeholders `${VAR_NAME}` (resolved by the runner before parsing).

### 4) Append upstream dataset to the current dataset

- File: [`examples/pipelines/14-union-by-name-append-upstream.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/14-union-by-name-append-upstream.yaml)

## Aggregations (group-by style)

- [`examples/pipelines/15-aggregation-group-by-key.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/15-aggregation-group-by-key.yaml) (sentiment → aggregatesentiment by key)
- [`examples/pipelines/16-aggregation-monthly.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/16-aggregation-monthly.yaml) (sentiment_monthly macro-stage)



