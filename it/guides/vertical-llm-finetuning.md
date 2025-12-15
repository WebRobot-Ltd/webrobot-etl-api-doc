---
title: Costruzione dataset per fine-tuning LLM (IT)
version: 1.0.0
description: "Guida completa (IT) per costruire dataset per fine-tuning LLM con policy No-CC"
---

# Costruzione dataset per fine-tuning LLM (IT)

Questa guida descrive come costruire dataset per fine-tuning (SFT) usando WebRobot ETL, con un focus su:

- aggregazione multi-sorgente
- pulizia/normalizzazione
- deduplicazione
- **governance licensing** (policy **No Creative Commons / No-CC**)

## Licensing & Data Governance (No-CC)

**Policy**: gli esempi di dataset di training in questa repository sono progettati per essere usati **senza fonti Creative Commons (CC*)**.

Usa solo contenuti:

- **customer-owned/internal**
- **public domain**
- **permissive non-CC** con diritti espliciti per training (ed eventualmente redistribuzione)

Pattern operativo consigliato:

- mantieni una **allowlist** (source_id → license_id → URL termini → usi consentiti)
- aggiungi campi di provenance per riga: `source`, `url`, `retrieved_at`, `license`
- escludi automaticamente fonti con licenza **unknown** o **CC***.

## Esempio concreto (No-CC)

- File pipeline: `examples/pipelines/23-llm-finetuning-dataset.yaml`

L’esempio combina:

1. **Customer-owned docs** (crawl da `${INTERNAL_DOCS_START_URL}`)
2. **Public domain docs** (CSV pre-curato: `${PUBLIC_DOMAIN_DOCS_CSV_PATH}`)
3. **Permissive non-CC code/docs** (CSV pre-curato: `${PERMISSIVE_CODE_DOCS_CSV_PATH}`)

Output: dataset CSV con colonne `instruction`, `input`, `output` (più metadata).

## Formati supportati (concetto)

- **Instruction-following** (Alpaca-style): `instruction`, `input`, `output`
- **Chat**: `messages[]`
- **Code completion**: `prompt`, `completion`
- **Q&A**: `question`, `context`, `answer`

Gli esempi YAML possono esportare CSV; la conversione finale a JSONL può essere effettuata downstream in Spark/Trino o nel training stack.


