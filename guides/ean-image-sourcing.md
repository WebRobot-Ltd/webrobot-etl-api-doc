---
title: EAN Image Sourcing Plugin
version: 1.0.0
description: Stages used by the EAN plugin pipeline and how CloudCredentials are resolved and injected at runtime
---

# EAN Image Sourcing Plugin

This page documents the **EAN Image Sourcing** Jersey plugin and the **pipeline stages** it uses internally.

The plugin exposes simplified endpoints under:

- `POST /webrobot/api/ean-image-sourcing/{country}/upload` (multipart CSV upload)
- `POST /webrobot/api/ean-image-sourcing/{country}/execute`
- `POST /webrobot/api/ean-image-sourcing/{country}/schedule`

Behind the scenes it manages Projects/Agents/Jobs and stores the YAML pipeline on the **Agent** (`pipelineYaml`).

---

## Default pipeline YAML (as shipped)

The plugin bootstraps Agents with a default pipeline similar to:

```yaml
pipeline:
  - stage: load_csv
    args:
      - path: "${INPUT_CSV_PATH}"
        header: "true"

  # Search by EAN (credentials can be provided via env vars injected from CloudCredentials)
  - stage: searchEngine
    args:
      - provider: "google"
        ean: "$EAN number"
        num_results: 10
        enrich: true
        image_search: false

  # Visit each result link with a browser
  - stage: visit
    args:
      - "$result_link"

  # Extract structured fields with LLM and cache selectors per template cluster
  - stage: iextract
    args:
      - selector: "body"
        method: "code"
      - "Extract product information from this e-commerce page: product name as product_name, current price as price (include currency symbol), brand as brand, EAN/GTIN/SKU code as ean_code, full product description as description, and all product image URLs (main product images, not logos) as product_image_urls. Also preserve the original input data: EAN number from CSV, item description, brand, search result title, snippet, matching score, and images from Google search results."
      - "prod_"

  # Score and select best images (LLM + heuristics)
  - stage: imageSimilarity
    args: []

output:
  path: "${OUTPUT_PARQUET_PATH}"
  mode: "overwrite"
  format: "parquet"
```

Notes:
- The plugin replaces `${INPUT_CSV_PATH}` / `${OUTPUT_PARQUET_PATH}` at runtime.
- Stages used above are documented in the general stage reference:
  - `load_csv`
  - `searchEngine`
  - `visit`
  - `iextract`
  - `imageSimilarity`

---

## Stage set used by the EAN plugin

- **`load_csv`**: reads the uploaded CSV from MinIO/S3 and creates the initial dataset.
- **`searchEngine`**: searches by EAN and enriches results; expects search credentials via env vars or CloudCredentials injection.
- **`visit`**: browser-based fetch for each row (uses Steel Dev if configured in the cluster).
- **`iextract`**: LLM extraction; uses selector-cache + template clustering to reduce repeated inference.
- **`imageSimilarity`**: ranks candidate images using LLM + heuristics (EAN in URL, context match, etc.).

---

## CloudCredentials: provider types + dynamic injection

### Provider types relevant to EAN

The EAN plugin auto-discovers (if not explicitly provided) these CloudCredential providers:

- **`GOOGLE_SEARCH`**: provides `GOOGLE_SEARCH_API_KEY` + `GOOGLE_SEARCH_ENGINE_ID`
- **`TOGETHERAI`**: provides `TOGETHERAI_API_KEY` (uses the generic credential `apiKey`)
- **`STEEL_DEV`**: provides `STEEL_DEV_API_KEY` (uses the generic credential `apiKey`)

### How the system chooses credentials at runtime

When you call the plugin execute endpoint, credential IDs can be provided in the request body:

- `cloudCredentialIds`: list of credential UUIDs (preferred)
- `cloudCredentialId`: single credential UUID (legacy)

If neither is provided, the plugin **auto-discovers** credentials by provider:

1. First try an enabled credential for the request Organization (`organizationId`),
2. then fall back to a global enabled credential (`organizationId = null`),
3. otherwise use the first enabled credential for that provider.

### How credentials are injected into the pipeline execution

During Spark job submission, the Kubernetes runner resolves CloudCredentials and injects them into the Spark driver/executor environment:

- `GOOGLE_SEARCH_API_KEY`
- `GOOGLE_SEARCH_ENGINE_ID`
- `BING_SEARCH_API_KEY`
- `STEEL_DEV_API_KEY`
- `TOGETHERAI_API_KEY`

If sensitive fields are encrypted, you can provide an encryption key:

- Header: `X-Encryption-Key` (plugin endpoints)
- Internally forwarded as `encryptionKey` for credential decryption during job submission.


