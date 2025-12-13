---
title: Partner tecnici (IT)
version: 1.0.0
description: Plugin API (Jersey) + plugin ETL (stage/resolver/action) + Python Extensions per AI-agent layer
---

# Partner tecnici (IT)

[English version](../../guides/technical-partners.md)

Questa guida spiega come estendere WebRobot in modo supportato:

- **Plugin Jersey (API)**: endpoint REST nel backend (es. EAN plugin).
- **Plugin ETL (Spark/runtime ETL)**: nuovi stage/resolver/actions usabili nelle pipeline YAML (es. `example-plugin`).
- **Python Extensions**: ideali per logica generata dinamicamente dall’AI-agent layer, con endpoint dedicato.

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

## Python Extensions (AI-agent layer)

Endpoint stabile oggi (inline YAML mode):
- `POST /webrobot/api/python-extensions/process-yaml`

Serve per aggiornare l’Agent con:
- `pipelineYaml`
- `pysparkCode` generato


