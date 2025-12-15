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
- `POST /webrobot/api/ean-image-sourcing/{country}/query` (query del dataset)
- `POST /webrobot/api/ean-image-sourcing/{country}/images` (immagini, opzionale base64)
- `GET  /webrobot/api/ean-image-sourcing/{country}/status`
- `GET  /webrobot/api/ean-image-sourcing/info`

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

## Download dataset + immagini per training / fit

Il plugin EAN è spesso usato per costruire dataset **vision+text** (catalog enrichment) che poi vengono consumati in fase di training/fit.

### 1) Scaricare righe dal dataset (API)

Non esiste un endpoint “download file” dedicato nel plugin; per scaricare dati usa:

- `POST /webrobot/api/ean-image-sourcing/{country}/query`

È il metodo consigliato per estrarre **subset filtrati** (es. lista EAN, colonne arricchite, top-N).

### 2) Scaricare immagini (URL o base64)

Usa:

- `POST /webrobot/api/ean-image-sourcing/{country}/images`

Campi chiave:
- `eans`: lista EAN
- `limit`: max immagini per EAN
- `includeBase64`: `true` per includere base64 (utile per training/fit senza fetch esterno)

Esempio (1 immagine migliore con base64 per EAN):

```bash
curl -X POST "${WEBROBOT_BASE_URL}/webrobot/api/ean-image-sourcing/italy/images" \
  -H "Content-Type: application/json" \
  -d '{
    "eans": ["5901234123457", "5901234123458"],
    "includeBase64": true,
    "limit": 1
  }'
```

### 3) Scaricare il dataset completo (storage path)

Se serve il dataset completo come file, usa gli endpoint generici:

- `GET /webrobot/api/datasets` (lista dataset)
- `GET /webrobot/api/datasets/{datasetId}` (contiene `storagePath` / `filePath` / `format`)

Poi scarica da MinIO/S3 con le credenziali di infrastruttura.


