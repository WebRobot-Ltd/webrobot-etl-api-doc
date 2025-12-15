---
title: Κατασκευή dataset για fine-tuning LLM (EL)
version: 1.0.0
description: "Πλήρης οδηγός (EL) για κατασκευή dataset fine-tuning LLM με πολιτική No-CC"
---

# Κατασκευή dataset για fine-tuning LLM (EL)

Αυτός ο οδηγός περιγράφει πώς να κατασκευάσετε datasets για fine-tuning (SFT) με WebRobot ETL, με έμφαση σε:

- multi-source aggregation
- καθαρισμό/normalization
- deduplication
- **governance licensing** (πολιτική **No Creative Commons / No-CC**)

## Licensing & Data Governance (No-CC)

**Πολιτική**: τα παραδείγματα dataset training σε αυτό το repository έχουν σχεδιαστεί για χρήση **χωρίς Creative Commons (CC*) πηγές**.

Χρησιμοποιήστε μόνο περιεχόμενο:

- **customer-owned/internal**
- **public domain**
- **permissive non-CC** με ρητά δικαιώματα για training (και, αν ισχύει, αναδιανομή)

Προτεινόμενο pattern:

- διατηρήστε **allowlist** (source_id → license_id → URL όρων → επιτρεπόμενες χρήσεις)
- προσθέστε provenance fields ανά γραμμή: `source`, `url`, `retrieved_at`, `license`
- αποκλείστε πηγές με **unknown** ή **CC*** license.

## Συγκεκριμένο παράδειγμα (No-CC)

- Pipeline file: `examples/pipelines/23-llm-finetuning-dataset.yaml`

Το παράδειγμα συνδυάζει:

1. **Customer-owned docs** (crawl από `${INTERNAL_DOCS_START_URL}`)
2. **Public domain docs** (pre-curated CSV: `${PUBLIC_DOMAIN_DOCS_CSV_PATH}`)
3. **Permissive non-CC code/docs** (pre-curated CSV: `${PERMISSIVE_CODE_DOCS_CSV_PATH}`)

Output: CSV dataset με στήλες `instruction`, `input`, `output` (και metadata).

## Υποστηριζόμενα formats (έννοια)

- **Instruction-following** (Alpaca-style): `instruction`, `input`, `output`
- **Chat**: `messages[]`
- **Code completion**: `prompt`, `completion`
- **Q&A**: `question`, `context`, `answer`

Τα YAML examples εξάγουν CSV· η τελική μετατροπή σε JSONL μπορεί να γίνει downstream (Spark/Trino ή training stack).


