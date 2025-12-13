---
title: Partner tecnici (IT)
version: 1.0.0
description: "Plugin API (Jersey) + plugin ETL (stage/resolver/action) + Python Extensions per AI-agent layer"
---

# Partner tecnici (IT)

[English version](../../guides/technical-partners.md)

Questa guida è per **admin** e **partner tecnici** che vogliono estendere WebRobot in modo supportato.

Esistono 3 meccanismi principali di estensione:

- **Plugin Jersey (API)**: endpoint REST nel backend (es. EAN plugin). Richiedono compilazione e deployment di JAR.
- **Plugin ETL (Spark/runtime ETL)**: nuovi stage/resolver/actions usabili nelle pipeline YAML (es. `example-plugin`). Richiedono compilazione e deployment di JAR.
- **Python Extensions**: meccanismo chiave per **auto-programmazione agentica** di stage personalizzati **senza compilazione**. Riservato ad admin e partner tecnici. Presupposto fondamentale per massima estendibilità richiesta dalla natura agentica di WebRobot.

## Plugin Jersey (API)

Pattern consigliato:
- risorse `@Path("/webrobot/api/<nome>")`
- bootstrap opzionale (`@PostConstruct`)
- gestione automatica di `Project` + `Agent(pipelineYaml)` + `Job`

## Plugin ETL (Spark)

Pattern consigliato:
- implementare `PipelineStage` e registrare in `StageRegistry`
- implementare `AttributeResolver` e registrare in `AttributeResolverRegistry`
- (opzionale) action factories per `fetch.traces`

Il modello di riferimento è `example-plugin` (registrazione centralizzata in `Plugin.registerAll()`).

## Python Extensions (meccanismo chiave per auto-programmazione agentica)

### Natura agentica e massima estendibilità

La **natura agentica** di WebRobot richiede **massimo livello di estendibilità** delle pipeline. Le **Python Extensions** sono il **presupposto fondamentale** per l'auto-programmazione di stage personalizzati da parte di AI agents, **senza la necessità di compilare plugin specifici**.

### Caratteristiche chiave

- **No compilation required**: Le Python extensions vengono caricate dinamicamente a runtime, senza necessità di compilare e distribuire plugin JAR
- **Auto-programmazione agentica**: Meccanismo ideale per AI agents che generano dinamicamente trasformazioni, resolver e stage personalizzati
- **Accesso riservato**: Funzionalità riservata a **admin** e **partner tecnici** per garantire sicurezza e controllo
- **Massima flessibilità**: Permette iterazione rapida e adattamento dinamico delle pipeline senza deployment di nuove versioni

### Endpoint dedicato (inline YAML mode)

Endpoint stabile oggi:
- `POST /webrobot/api/python-extensions/process-yaml`

**Autenticazione**: Richiede API key con privilegi di **admin** o **partner tecnico**.

Serve per aggiornare l'Agent con:
- `pipelineYaml`
- `pysparkCode` generato


