---
title: Plugins & επεκτασιμότητα (EL)
version: 1.0.0
description: "Πώς να επεκτείνετε το WebRobot ETL: stages, attribute resolvers, custom actions και API plugins (χωρίς λεπτομέρειες core engine)"
---

# Plugins & επεκτασιμότητα (EL)

Το WebRobot έχει σχεδιαστεί ώστε να είναι **επεκτάσιμο**, για να μπορείτε να παραδίδετε vertical capabilities χωρίς fork του core engine.

Αυτός ο οδηγός εξηγεί **τι** μπορεί να επεκταθεί και **πώς** να σχεδιάσετε μια υποστηριζόμενη plugin ενσωμάτωση, αποφεύγοντας σκόπιμα να εκθέσει λεπτομέρειες υλοποίησης του core.

> **Σημαντικό (εμπιστευτικότητα / σταθερότητα)**: δεν δημοσιεύουμε ακόμη implementational examples. Μέχρι το plugin system να μπορεί να στοχεύσει μια πιο αφηρημένη και σταθερή integration interface, η τεκμηρίωση παραμένει στο **contract level** (συμπεριφορά από YAML/API).

## Επίπεδα επεκτασιμότητας

### 1) ETL runtime plugins (YAML)

Επεκτείνουν τις YAML pipelines προσθέτοντας:

- **Stages**: νέα `stage: <name>` μέσα σε `pipeline:`
- **Attribute resolvers**: νέα `method: <name>` μέσα σε `extract` / `flatSelect`
- **Custom actions**: νέες ενέργειες σε `fetch.traces[].action`

### 2) API plugins (endpoints)

Προσθέτουν **REST endpoints** που “productize” pipelines/jobs.

Συνήθεις ευθύνες:
- απλοποιημένο API (`upload` / `execute` / `status` / `query` / `images`)
- orchestration & scheduling
- tenant/org rules και credentials injection
- domain-specific validation/defaults

Παράδειγμα: EAN plugin (βλ. `el/guides/ean-image-sourcing.md`).

### 3) Python Extensions

Επιτρέπουν γρήγορο iteration με `python_row_transform:<name>` σε runtime (cleaning/normalization/enrichment).

## Τι μπορείτε να επεκτείνετε (contracts)

### A) Νέο stage

User-facing contract:
- σταθερό όνομα
- τεκμηριωμένα `args`
- transformation του τρέχοντος dataset/plan

### B) Νέος attribute resolver

User-facing contract:
- `method: "<resolver>"`
- προαιρετικό `args: [...]`
- output σε `as: "<field>"`

### C) Νέα custom action (trace)

User-facing contract:
- `{ action: "<name>", params: { ... } }` σε `fetch.traces`
- ordered execution και τεκμηριωμένα params

### D) Νέο endpoint (API plugin)

User-facing contract:
- σταθερά paths κάτω από `/webrobot/api/<plugin>/...`
- schemas σε OpenAPI
- scopes/tenant isolation
- CloudCredentials support όπου χρειάζεται

## Ασφάλεια, licensing, εμπιστευτικότητα

- credentials μόνο μέσω CloudCredentials/secure injection
- τεκμηρίωση δικαιωμάτων χρήσης πηγών (ειδικά για training/fit datasets)
- αποφυγή διαρροής core engine internals μέχρι να σταθεροποιηθεί πιο αφηρημένη integration interface

## Χρήσιμα links

- `el/guides/pipeline-stages.md`
- `el/guides/pipeline-examples.md`
- `el/guides/ean-image-sourcing.md`
- `guides/technical-partners.md`


