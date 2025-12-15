---
title: Plugin & estendibilità (IT)
version: 1.0.0
description: "Come estendere WebRobot ETL: stages, attribute resolver, custom actions e plugin API (senza dettagli implementativi del core)"
---

# Plugin & estendibilità (IT)

WebRobot è progettato per essere **estendibile** così da rilasciare capacità verticali senza fork del core engine.

Questa guida spiega **cosa** è estendibile e **come** pianificare un’integrazione plugin in modo supportato, evitando intenzionalmente di esporre dettagli implementativi del core.

> **Importante (confidenzialità / stabilità)**: non pubblichiamo ancora esempi implementativi. Finché il sistema plugin non potrà referenziare un’interfaccia di integrazione più astratta e stabile, la documentazione rimane a livello **contrattuale** (comportamento da YAML/API).

## Livelli di estensione

### 1) Plugin ETL runtime (YAML)

Estendono ciò che una pipeline YAML può fare aggiungendo:

- **Stages**: nuovi `stage: <name>` in `pipeline:`
- **Attribute resolver**: nuovi `method: <name>` in `extract` / `flatSelect`
- **Custom actions**: nuove azioni in `fetch.traces[].action`

### 2) Plugin API (endpoint)

Aggiungono **endpoint REST** che “productizzano” pipeline e job.

Responsabilità tipiche:
- API semplificata (`upload` / `execute` / `status` / `query` / `images`)
- orchestrazione job e scheduling
- regole tenant/org e injection credenziali
- validazione domain-specific

Esempio: plugin EAN (vedi `it/guides/ean-image-sourcing.md`).

### 3) Python Extensions (trasformazioni dinamiche)

Permettono iterazione rapida registrando `python_row_transform:<name>` a runtime (per cleaning/normalization/enrichment).

## Cosa puoi estendere (contratti)

### A) Nuovo stage

Contratto lato utente:
- nome stabile
- `args` (lista) con schema documentato
- trasformazione del dataset/plan corrente

### B) Nuovo attribute resolver

Contratto lato utente:
- `method: "<resolver>"`
- `args: [...]` opzionale
- output assegnato a `as: "<field>"`

### C) Nuova custom action (trace)

Contratto lato utente:
- `{ action: "<name>", params: { ... } }` in `fetch.traces`
- esecuzione ordinata e parametri documentati

### D) Nuovo endpoint (plugin API)

Contratto lato utente:
- path stabili sotto `/webrobot/api/<plugin>/...`
- request/response in OpenAPI
- auth scopes e isolamento tenant
- supporto CloudCredentials dove necessario

Pattern consigliato:
- `upload`, `execute`, `status`, `query`, e un pattern per download (query o storagePath via dataset API).

## Sicurezza, licensing, confidenzialità

- credenziali solo via CloudCredentials/injection sicura
- documentare i diritti d’uso delle fonti (soprattutto per dataset training/fit)
- non esporre dettagli del core engine finché non esiste un’interfaccia di integrazione più astratta

## Link utili

- `it/guides/pipeline-stages.md`
- `it/guides/pipeline-examples.md`
- `it/guides/ean-image-sourcing.md`
- `guides/technical-partners.md`


