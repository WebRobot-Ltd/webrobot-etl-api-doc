---
title: Παραδείγματα pipeline (EL)
version: 1.0.0
description: Παραδείγματα YAML έτοιμα για αντιγραφή, ευθυγραμμισμένα με τον τρέχοντα parser
---

# Παραδείγματα pipeline (EL)

[English version](../../guides/pipeline-examples.md) | [Versione italiana](../../it/guides/pipeline-examples.md)

Τα παραδείγματα "runnable" βρίσκονται στο repo κάτω από `examples/pipelines/`.

## Κατάλογος παραδειγμάτων

- [`examples/pipelines/01-static-books.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/01-static-books.yaml)
- [`examples/pipelines/02-dynamic-quotes.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/02-dynamic-quotes.yaml)
- [`examples/pipelines/03-iextract-prompt-only.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/03-iextract-prompt-only.yaml)
- [`examples/pipelines/04-attribute-resolvers.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/04-attribute-resolvers.yaml)
- [`examples/pipelines/05-python-row-transforms.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/05-python-row-transforms.yaml)
- [`examples/pipelines/06-io-load-save-csv.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/06-io-load-save-csv.yaml)
- [`examples/pipelines/07-searchengine-ean-enrich.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/07-searchengine-ean-enrich.yaml)
- [`examples/pipelines/08-fetch-traces-browser-actions.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/08-fetch-traces-browser-actions.yaml)
- [`examples/pipelines/09-multi-source-seeds-union-dedup.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/09-multi-source-seeds-union-dedup.yaml)  # ένωση seed lists + dedup
- [`examples/pipelines/10-multi-source-results-union-dedup.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/10-multi-source-results-union-dedup.yaml) # ένωση αποτελεσμάτων πολλαπλών πηγών + dedup
- [`examples/pipelines/11-vertical-source-a-offers.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/11-vertical-source-a-offers.yaml)          # πηγή A (fetch+extract)
- [`examples/pipelines/12-vertical-source-b-offers.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/12-vertical-source-b-offers.yaml)          # πηγή B (fetch+extract)
- [`examples/pipelines/13-vertical-stitch-union-dedup-offers.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/13-vertical-stitch-union-dedup-offers.yaml) # stitching (load_union + dedup)
- [`examples/pipelines/14-union-by-name-append-upstream.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/14-union-by-name-append-upstream.yaml)     # append upstream dataset
- [`examples/pipelines/15-aggregation-group-by-key.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/15-aggregation-group-by-key.yaml)          # aggregation by-key
- [`examples/pipelines/16-aggregation-monthly.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/16-aggregation-monthly.yaml)               # monthly aggregation

Για την πλήρη εξήγηση κάθε παραδείγματος, χρησιμοποιήστε την αγγλική σελίδα ή ανοίξτε απευθείας τα αρχεία YAML.

