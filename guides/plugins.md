---
title: Plugins & Extensibility
version: 1.0.0
description: "How to extend WebRobot ETL safely: stages, attribute resolvers, custom actions, and API plugins (no core engine implementation details)"
---

# Plugins & Extensibility

WebRobot is designed to be **extensible** so teams can ship vertical capabilities without forking the core engine.

This guide explains **what can be extended** and **how to plan a supported plugin integration**, while intentionally **not exposing core engine implementation details**.

> **Important (confidentiality / stability)**: We do not publish implementation-level examples yet. Until the plugin system can target a more abstract, stable integration interface, this documentation stays at the **conceptual contract level** (what you can do + how it behaves from the user/API perspective).

## Extensibility layers

### 1) ETL Runtime Plugins (YAML-level)

These plugins extend what a YAML pipeline can do by adding:

- **Stages**: new `stage: <name>` entries usable in `pipeline:`
- **Attribute resolvers**: new `method: <name>` resolvers usable inside `extract` / `flatSelect`
- **Custom actions**: new `fetch.traces[].action` entries (browser/action layer)

This is the mechanism used to add domain primitives (e.g. image scoring, clustering, specialized parsers), while keeping pipelines declarative.

### 2) API Plugins (endpoint-level)

These plugins add **new REST endpoints** that wrap and productize pipelines.

Typical responsibilities:
- expose a simplified API (e.g. `upload` / `execute` / `status` / `query` / `images`)
- orchestrate jobs and handle scheduling
- apply tenant/org rules and credentials injection
- provide domain-specific validation and defaults

Example: the EAN plugin (see `guides/ean-image-sourcing.md`).

### 3) Python Extensions (dynamic transforms)

Python extensions enable controlled, rapid iteration by registering `python_row_transform:<name>` functions at runtime.
They are ideal for data cleaning/normalization/enrichment that changes frequently.

## What you can extend (contracts)

### A) Add a new Stage

**User-facing contract**:
- a stage has a **stable name**
- it accepts a list of **args**
- it transforms the current dataset or navigation plan

**Documentation requirements**:
- stage name + supported aliases
- `args` schema (positional / map), defaults, validation rules
- input/output schema changes
- operational constraints (requires browser, requires credentials, rate limits, etc.)

### B) Add a new Attribute Resolver

**User-facing contract**:
- used from `extract` / `flatSelect` as `method: "<resolver>"`
- may accept optional `args: [...]`
- returns a value (scalar/string/number/map/list) assigned to `as: "<field>"`

**Documentation requirements**:
- resolver name + expected input (selector vs field)
- output type(s)
- optional args + examples at YAML level (no code)

### C) Add a new Custom Action (trace)

**User-facing contract**:
- used under `fetch.traces` as `{ action: "<name>", params: { ... } }`
- executed in order before the pipeline starts (or as part of navigation flows)

**Documentation requirements**:
- action name
- required/optional `params`
- safety considerations (timeouts, idempotency, rate limiting)

### D) Add/extend an Endpoint (API plugin)

**User-facing contract**:
- stable endpoint paths under `/webrobot/api/<plugin>/...`
- request/response schemas in OpenAPI
- auth scopes and tenant isolation
- support for CloudCredentials selection/injection (where relevant)

**Recommended endpoint set (pattern)**:
- `POST .../upload` (ingest data)
- `POST .../execute` (run a job)
- `GET  .../status` (observe last run)
- `POST .../query` (query latest dataset / filtered retrieval)
- `POST .../download` or “dataset discovery + storagePath” pattern

## Compatibility & versioning

- **Semantic versioning**: bump minor for backward-compatible additions; bump major for breaking changes.
- **Stable names**: treat `stage`, resolver `method`, and trace `action` names as public API.
- **Deprecation**: keep deprecated aliases for at least one minor cycle and document migration.

## Security, licensing, and confidentiality

- **No secret leakage**: all credentials must be injected via CloudCredentials/secure runtime mechanisms; never hardcode keys in YAML/docs.
- **Data licensing**: plugins must document expected data sources and required rights (especially for training/fit datasets).
- **Least privilege**: enforce scopes for plugin endpoints; separate read/query from execute/upload.
- **Implementation confidentiality**: do not publish internal class names, registry wiring, or engine internals until the abstract integration interface is stable.

## Where to go next

- **Stage syntax and YAML constraints**: `guides/pipeline-stages.md`
- **Runnable pipelines**: `guides/pipeline-examples.md`
- **EAN plugin (API + dataset/images retrieval)**: `guides/ean-image-sourcing.md`
- **Partner/technical integration overview**: `guides/technical-partners.md`


