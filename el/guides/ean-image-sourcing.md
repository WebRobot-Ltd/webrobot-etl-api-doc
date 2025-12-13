---
title: Plugin EAN Image Sourcing (EL)
version: 1.0.0
description: Stages που χρησιμοποιούνται από το plugin EAN και πώς επιλύονται/ενέχονται οι CloudCredentials κατά το runtime
---

# Plugin EAN Image Sourcing (EL)

[English version](../../guides/ean-image-sourcing.md) | [Versione italiana](../../it/guides/ean-image-sourcing.md)

Αυτή η σελίδα τεκμηριώνει το plugin Jersey `ean-image-sourcing` και την pipeline που εκτελεί.

## Κύρια endpoints

- `POST /webrobot/api/ean-image-sourcing/{country}/upload` (CSV upload)
- `POST /webrobot/api/ean-image-sourcing/{country}/execute`
- `POST /webrobot/api/ean-image-sourcing/{country}/schedule`

## Stage-set που χρησιμοποιείται από την pipeline

Συνήθως:
- `load_csv`
- `searchEngine`
- `visit`
- `iextract`
- `imageSimilarity`

## CloudCredentials: provider + δυναμική injection

Απαιτούμενοι providers (auto-discovery αν δεν περαστούν ρητά):
- `GOOGLE_SEARCH` → `GOOGLE_SEARCH_API_KEY`, `GOOGLE_SEARCH_ENGINE_ID`
- `TOGETHERAI` → `TOGETHERAI_API_KEY`
- `STEEL_DEV` → `STEEL_DEV_API_KEY`

Τρόπος:
- στο body μπορείτε να περάσετε `cloudCredentialIds` (λίστα) ή `cloudCredentialId` (legacy)
- αν δεν υπάρχουν, το plugin αναζητά ενεργοποιημένες διαπιστευτήριες για provider (πρώτα org-specific, μετά global, μετά πρώτη διαθέσιμη)
- κατά την υποβολή Spark, οι διαπιστευτήριες ενέχονται ως env σε driver/executor
- αν τα πεδία είναι κρυπτογραφημένα, μπορείτε να περάσετε `X-Encryption-Key` στα headers του plugin

