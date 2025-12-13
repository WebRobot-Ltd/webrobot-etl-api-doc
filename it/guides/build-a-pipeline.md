---
title: Costruire una pipeline (IT)
version: 1.0.0
description: Guida per creare pipeline ETL in YAML e avviarle tramite WebRobot ETL API
---

# Costruire una pipeline (IT)

[English version](../../guides/build-a-pipeline.md)

Questa guida spiega come creare pipeline ETL usando YAML e come eseguirle via API.

## Struttura del YAML

```yaml
fetch:                  # opzionale
  url: "https://example.com"
  traces:               # opzionale (azioni browser)
    - { action: "wait", params: { seconds: 1 } }

pipeline:               # obbligatorio
  - stage: join
    args: [ "a.product-link", "LeftOuter" ]
  - stage: extract
    args:
      - { selector: "h1", method: "text", as: "title" }
```

## API: dove “vive” la pipeline

**Non esiste** un endpoint `/webrobot/api/pipelines`.

La pipeline YAML viene salvata sull’**Agent** (`pipelineYaml`) ed eseguita creando un **Job** che punta a quell’Agent.

### 1) Crea/Aggiorna Agent con `pipelineYaml`

```bash
curl -X POST https://api.webrobot.eu/api/webrobot/api/agents \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-agent",
    "categoryId": "1",
    "pipelineYaml": "pipeline:\n  - stage: join\n    args: [\"a.product-link\"]\n  - stage: extract\n    args:\n      - { selector: \"h1\", method: \"text\", as: \"title\" }",
    "enabled": true
  }'
```

### 2) Crea Job che usa l’Agent

```bash
curl -X POST https://api.webrobot.eu/api/webrobot/api/projects/id/your-project-id/jobs \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{ "name": "my-job", "agentId": "123" }'
```

### 3) Esegui Job

```bash
curl -X POST https://api.webrobot.eu/api/webrobot/api/projects/id/your-project-id/jobs/your-job-id/execute \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{ "parameters": { "limit": 100 } }'
```

## Approfondimenti

- [Riferimento stage pipeline (IT)](pipeline-stages.md)
- [Esempi pipeline (IT)](pipeline-examples.md)
- [Partner tecnici (IT)](technical-partners.md)


