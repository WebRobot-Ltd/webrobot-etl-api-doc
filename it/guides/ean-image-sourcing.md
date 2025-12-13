---
title: Plugin EAN Image Sourcing (IT)
version: 1.0.0
description: Stage usati dal plugin EAN e come vengono risolte/iniettate le CloudCredentials a runtime
---

# Plugin EAN Image Sourcing (IT)

[English version](../../guides/ean-image-sourcing.md)

Questa pagina documenta il plugin Jersey `ean-image-sourcing` e la pipeline che esegue.

## Endpoint principali

- `POST /webrobot/api/ean-image-sourcing/{country}/upload` (CSV upload)
- `POST /webrobot/api/ean-image-sourcing/{country}/execute`
- `POST /webrobot/api/ean-image-sourcing/{country}/schedule`

## Stage-set usato dalla pipeline

Tipicamente:
- `load_csv`
- `searchEngine`
- `visit`
- `iextract`
- `imageSimilarity`

## CloudCredentials: provider + injection dinamica

Provider richiesti (auto-discovery se non passati esplicitamente):
- `GOOGLE_SEARCH` → `GOOGLE_SEARCH_API_KEY`, `GOOGLE_SEARCH_ENGINE_ID`
- `TOGETHERAI` → `TOGETHERAI_API_KEY`
- `STEEL_DEV` → `STEEL_DEV_API_KEY`

Modalità:
- nel body puoi passare `cloudCredentialIds` (lista) o `cloudCredentialId` (legacy)
- se non presenti, il plugin cerca credenziali abilitate per provider (prima org-specific, poi global, poi prima disponibile)
- in fase di submit Spark, le credenziali vengono iniettate come env su driver/executor
- se i campi sono cifrati, puoi passare `X-Encryption-Key` negli header del plugin


