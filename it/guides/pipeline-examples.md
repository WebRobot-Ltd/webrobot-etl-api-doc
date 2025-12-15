---
title: Esempi pipeline (IT)
version: 1.0.0
description: Esempi YAML pronti da copiare, allineati al parser attuale
---

# Esempi pipeline (IT)

[English version](../../guides/pipeline-examples.md)

Gli esempi “runnable” sono nel repo sotto `examples/pipelines/`.

## Elenco esempi

- [`examples/pipelines/01-static-books.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/01-static-books.yaml)
- [`examples/pipelines/02-dynamic-quotes.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/02-dynamic-quotes.yaml)
- [`examples/pipelines/03-iextract-prompt-only.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/03-iextract-prompt-only.yaml)
- [`examples/pipelines/04-attribute-resolvers.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/04-attribute-resolvers.yaml)
- [`examples/pipelines/05-python-row-transforms.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/05-python-row-transforms.yaml)
- [`examples/pipelines/06-io-load-save-csv.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/06-io-load-save-csv.yaml)
- [`examples/pipelines/07-searchengine-ean-enrich.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/07-searchengine-ean-enrich.yaml)
- [`examples/pipelines/08-fetch-traces-browser-actions.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/08-fetch-traces-browser-actions.yaml)
- [`examples/pipelines/09-multi-source-seeds-union-dedup.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/09-multi-source-seeds-union-dedup.yaml)  # unione insiemistica seed + dedup
- [`examples/pipelines/10-multi-source-results-union-dedup.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/10-multi-source-results-union-dedup.yaml) # unione risultati multi-sorgente + dedup
- [`examples/pipelines/11-vertical-source-a-offers.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/11-vertical-source-a-offers.yaml)         # pipeline sorgente A (fetch+extract)
- [`examples/pipelines/12-vertical-source-b-offers.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/12-vertical-source-b-offers.yaml)         # pipeline sorgente B (fetch+extract)
- [`examples/pipelines/13-vertical-stitch-union-dedup-offers.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/13-vertical-stitch-union-dedup-offers.yaml) # stitching (load_union + dedup)
- [`examples/pipelines/14-union-by-name-append-upstream.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/14-union-by-name-append-upstream.yaml)    # append upstream dataset
- [`examples/pipelines/15-aggregation-group-by-key.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/15-aggregation-group-by-key.yaml)         # aggregazione by-key
- [`examples/pipelines/16-aggregation-monthly.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/16-aggregation-monthly.yaml)              # aggregazione mensile
- [`examples/pipelines/17-single-pipeline-multi-source-union.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/17-single-pipeline-multi-source-union.yaml)  # multi-source con store/reset/union_with
- [`examples/pipelines/18-single-pipeline-alternative-syntax.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/18-single-pipeline-alternative-syntax.yaml)     # alternativa multi-source
- [`examples/pipelines/19-price-comparison-5-sites.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/19-price-comparison-5-sites.yaml)                      # price comparison (5 siti) – output row-level + pivot downstream
- [`examples/pipelines/20-sports-betting-5-bookmakers.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/20-sports-betting-5-bookmakers.yaml)                # odds aggregation (5 bookmaker) – placeholder/compliance
- [`examples/pipelines/21-surebet-intelligent-extraction.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/21-surebet-intelligent-extraction.yaml)            # surebet – extraction intelligente, calcolo downstream
- [`examples/pipelines/22-real-estate-arbitrage-clustering.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/22-real-estate-arbitrage-clustering.yaml)        # real estate arbitrage + clustering
- [`examples/pipelines/23-llm-finetuning-dataset.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/23-llm-finetuning-dataset.yaml)                        # dataset fine-tuning LLM (No-CC policy)
- [`examples/pipelines/24-portfolio-management-90d-prediction.yaml`](https://github.com/WebRobot-Ltd/webrobot-etl-api-doc/blob/master/examples/pipelines/24-portfolio-management-90d-prediction.yaml)  # portfolio management 90g

Per la spiegazione completa di ogni esempio, usa la pagina in inglese o apri direttamente i file YAML.

## Note di compliance (importante)

- Gli esempi che citano siti/brand esterni usano spesso **URL placeholder** o pattern generici: usa solo fonti per cui hai autorizzazione.
- Per i dataset di training LLM, la guida di riferimento (`vertical-llm-finetuning.md`) applica una policy **No Creative Commons (No-CC)**: non usare contenuti CC* per training/redistribuzione se non espressamente autorizzato.


