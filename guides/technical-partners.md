---
title: Technical Partners
version: 1.0.0
description: "How to extend WebRobot in a supported way: API plugins (endpoints), ETL runtime plugins (stages/resolvers/actions), and Python Extensions"
---

# Technical Partners

This section is for **admins** and **technical partners** who want to extend WebRobot in a **supported** way.

There are three primary extension mechanisms:

- **API Plugins (endpoints)**: add REST endpoints to the backend (example: the EAN plugin). Typically delivered as a JAR and deployed server-side.
- **ETL Runtime Plugins**: add stages/resolvers/actions usable from YAML pipelines (example: `example-plugin`). Typically delivered as a JAR and loaded by the ETL runtime.
- **Python Extensions**: controlled mechanism for registering dynamic transforms (`python_row_transform:<name>`) without compiling a new plugin. Intended for admin/partner usage.

> **Note (confidentiality / stability)**: This documentation focuses on **behavioral contracts** and recommended patterns. We intentionally avoid core engine implementation details.

---

## 1) API Plugins (endpoint layer) — “EAN-style”

### What it is
An API plugin is a set of REST endpoints mounted under `/webrobot/api/<plugin-name>/...` that productizes one or more pipelines/jobs.

### Recommended pattern
- **Bootstrap**: create/ensure domain resources (e.g., project/agent/job templates) and defaults.
- **Simplified endpoints**: `upload`, `execute`, `schedule`, `status`, `query`, domain-specific endpoints (e.g., `images`).
- **Credential handling**: accept explicit `cloudCredentialIds` or use provider-based discovery; inject runtime env vars during execution.

See also: [EAN Image Sourcing Plugin](ean-image-sourcing.md).

---

## 2) ETL Runtime Plugins (YAML layer) — “example-plugin style”

### What it is
An ETL runtime plugin extends the pipeline runner with:
- **Pipeline stages** usable as `stage: ...`
- **Attribute resolvers** usable as `method: ...` inside `extract` / `flatSelect`
- **Action factories** usable as `fetch.traces[].action`

### Documentation checklist for a new stage/resolver/action
- Stable public name(s) and aliases
- Arguments schema + defaults + validation rules
- Input/output schema behavior
- Operational requirements (browser, credentials, rate limits)
- At least one runnable YAML example (no internal code details)

---

## 3) Python Extensions (dynamic transforms)

### Why this exists
Agentic workflows often require fast iteration on normalization/enrichment logic. Python Extensions provide a controlled way to register transforms without shipping a new JAR.

### Stable API flow (inline YAML mode)
There is a dedicated endpoint to process YAML and generate/update an Agent’s Python registration code:

- `POST /webrobot/api/python-extensions/process-yaml`

Typical payload:
- `agentId`
- `yamlContent` (pipeline YAML + optional `python_extensions` for code generation)

**Authentication**: requires an API key with admin/partner privileges.

> Note: some DB-based extension flows may depend on the specific build; the stable flow is `process-yaml` (inline).


