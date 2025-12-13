---
title: Documentazione WebRobot ETL API (Italiano)
version: 1.0.0
description: Guide e riferimento API per costruire e gestire pipeline ETL in YAML
---

# WebRobot ETL API – Documentazione (IT)

[English version](../index.md)

Questa è la versione **in italiano** della documentazione.

## Informazioni su WebRobot

**WebRobot** è un'**infrastruttura dati nativa Spark e API-first** per costruire **pipeline ETL agentiche** e **prodotti dati**.

Questa documentazione copre il **componente ETL** di WebRobot, che fornisce:

- **Elaborazione nativa Spark**: Costruito su Apache Spark per l'elaborazione dati scalabile
- **Architettura API-first**: Gestisci pipeline, progetti e job tramite REST API
- **Capacità agentiche**: Stage intelligenti basati su LLM per web scraping adattivo ed estrazione dati
- **Framework estendibile**: Plugin personalizzati, stage, resolver ed estensioni Python

## Integrazione AI Agent & Protocollo MCP

Questa documentazione funge da **base di conoscenza di riferimento** per agenti AI e strumenti di sviluppo:

### 🤖 Supporto AI Agent

Questa documentazione è progettata per essere utilizzata da assistenti AI e agenti di codifica, inclusi:

- **Cursor AI**: Assistente AI integrato per generazione codice e creazione pipeline
- **ChatGPT**: Documentazione di riferimento per le capacità ETL di WebRobot
- **Claude Desktop**: Base di conoscenza per comprendere architettura e API di WebRobot
- **Agente di sviluppo integrato**: Agente AI integrato in WebRobot per generazione e ottimizzazione automatica di pipeline

### 🔌 Model Context Protocol (MCP)

Tutte le funzionalità ETL di WebRobot sono esposte tramite **endpoint MCP (Model Context Protocol)**, abilitando:

- **Integrazione AI standardizzata**: Interfaccia consistente per agenti AI per interagire con WebRobot
- **Function calling**: Gli agenti AI possono invocare operazioni WebRobot tramite strumenti MCP
- **Assistenza context-aware**: Gli agenti possono interrogare schemi pipeline, capacità degli stage e specifiche API
- **Generazione automatica pipeline**: Gli agenti AI possono creare, validare ed eseguire pipeline programmaticamente

Ogni funzionalità documentata qui è accessibile sia tramite REST API che endpoint MCP, garantendo integrazione fluida con flussi di lavoro di sviluppo basati su AI.

## Inizia subito

- **[Costruire una pipeline](guides/build-a-pipeline.md)** (IT)
- **[Riferimento stage pipeline](guides/pipeline-stages.md)** (IT)
- **[Esempi pipeline](guides/pipeline-examples.md)** (IT)
- **[Plugin EAN Image Sourcing](guides/ean-image-sourcing.md)** (IT)
- **[Partner tecnici](guides/technical-partners.md)** (IT)

## Nota sulla lingua

Per partire subito, la documentazione tecnica più dettagliata resta spesso in inglese; la versione italiana è mantenuta allineata alle parti più operative e ai flussi API principali.


