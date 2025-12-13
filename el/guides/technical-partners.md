---
title: Τεχνικοί συνεργάτες (EL)
version: 1.0.0
description: Plugin API (Jersey) + plugin ETL (stage/resolver/action) + Python Extensions για AI-agent layer
---

# Τεχνικοί συνεργάτες (EL)

[English version](../../guides/technical-partners.md) | [Versione italiana](../../it/guides/technical-partners.md)

Αυτός ο οδηγός εξηγεί πώς να επεκτείνετε το WebRobot με υποστηριζόμενο τρόπο:

- **Plugin Jersey (API)**: REST endpoints στο backend (π.χ. EAN plugin).
- **Plugin ETL (Spark/SpookyStuff)**: νέα stages/resolver/actions χρησιμοποιήσιμα στις pipelines YAML (π.χ. `example-plugin`).
- **Python Extensions**: ιδανικά για λογική που δημιουργείται δυναμικά από το AI-agent layer, με αφοσιωμένο endpoint.

## Plugin Jersey (API)

Συνιστώμενο pattern:
- πόροι `@Path("/webrobot/api/<όνομα>")`
- προαιρετικό bootstrap (`@PostConstruct`)
- αυτόματη διαχείριση `Project` + `Agent(pipelineYaml)` + `Job`

## Plugin ETL (Spark)

Συνιστώμενο pattern:
- υλοποίηση `PipelineStage` και εγγραφή στο `StageRegistry`
- υλοποίηση `AttributeResolver` και εγγραφή στο `AttributeResolverRegistry`
- (προαιρετικό) action factories για `fetch.traces`

Το μοντέλο αναφοράς είναι το `example-plugin` (κεντρική εγγραφή στο `Plugin.registerAll()`).

## Python Extensions (AI-agent layer)

Σταθερό endpoint σήμερα (inline YAML mode):
- `POST /webrobot/api/python-extensions/process-yaml`

Χρησιμεύει για ενημέρωση του Agent με:
- `pipelineYaml`
- `pysparkCode` που δημιουργείται

