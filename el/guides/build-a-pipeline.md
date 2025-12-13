---
title: Κατασκευή pipeline (EL)
version: 1.0.0
description: Οδηγός για τη δημιουργία pipeline ETL σε YAML και εκτέλεσή τους μέσω WebRobot ETL API
---

# Κατασκευή pipeline (EL)

[English version](../../guides/build-a-pipeline.md) | [Versione italiana](../../it/guides/build-a-pipeline.md)

Αυτός ο οδηγός εξηγεί πώς να δημιουργήσετε pipeline ETL χρησιμοποιώντας YAML και πώς να τις εκτελέσετε μέσω API.

> Το **WebRobot** είναι μια **υποδομή δεδομένων native Spark, API-first** για την κατασκευή **agentic pipeline ETL** και **προϊόντων δεδομένων**. Αυτό το συστατικό ETL παρέχει επεκτάσιμη επεξεργασία δεδομένων, έξυπνη εξαγωγή δεδομένων από το web και επεκτάσιμη διαχείριση pipeline.

## Δομή YAML

```yaml
fetch:                  # προαιρετικό
  url: "https://example.com"
  traces:               # προαιρετικό (ενέργειες browser)
    - { action: "wait", params: { seconds: 1 } }

pipeline:               # υποχρεωτικό
  - stage: join
    args: [ "a.product-link", "LeftOuter" ]
  - stage: extract
    args:
      - { selector: "h1", method: "text", as: "title" }
```

## API: πού "ζει" η pipeline

**Δεν υπάρχει** endpoint `/webrobot/api/pipelines`.

Η pipeline YAML αποθηκεύεται στον **Agent** (`pipelineYaml`) και εκτελείται δημιουργώντας ένα **Job** που δείχνει σε αυτόν τον Agent.

### 1) Δημιουργία/Ενημέρωση Agent με `pipelineYaml`

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

### 2) Δημιουργία Job που χρησιμοποιεί τον Agent

```bash
curl -X POST https://api.webrobot.eu/api/webrobot/api/projects/id/your-project-id/jobs \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{ "name": "my-job", "agentId": "123" }'
```

### 3) Εκτέλεση Job

```bash
curl -X POST https://api.webrobot.eu/api/webrobot/api/projects/id/your-project-id/jobs/your-job-id/execute \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{ "parameters": { "limit": 100 } }'
```

## Περαιτέρω ανάγνωση

- [Αναφορά stages pipeline (EL)](pipeline-stages.md)
- [Παραδείγματα pipeline (EL)](pipeline-examples.md)
- [Τεχνικοί συνεργάτες (EL)](technical-partners.md)

