---
title: Implementazioni future (Roadmap) (IT)
version: 1.0.0
description: "Direzioni future: ingestion streaming (IoT), smart city & mobility, flotte droni, operazioni real-time agentiche"
---

# Implementazioni future (Roadmap) (IT)

Questa pagina raccoglie direzioni di sviluppo **future** per WebRobot in domini che richiedono **ingestion streaming**, **analitiche real-time** e **decision loop operativi**.

> Nota: documento di roadmap architetturale. Evita intenzionalmente dettagli implementativi del core engine.

## 1) Fonti in streaming (IoT)

### Fonti target
- MQTT broker (sensori, contatori, building automation)
- Kafka/Pulsar topic (event bus, city data platform)
- AMQP/RabbitMQ (integrazioni legacy)
- Webhook / HTTP event collector (device gateway)

### Modello canonico (concetto)
- **event_time** vs **ingest_time**
- **device_id / asset_id**
- **geo** (lat/lon + opzionale geohash)
- **payload telemetria** (metriche tipizzate + raw JSON)
- **provenance**: source, tenant, schema version

### Capability chiave
- Validazione schema + evoluzione (Schema Registry model)
- Eventi late/out-of-order (watermark)
- Dedup `(device_id, event_time, sequence_id)`
- Quality checks (gap, outlier, drift)

## 2) Smart city & mobility

### Use case
- Traffico e congestione
- Trasporto pubblico (es. GTFS-RT)
- Parking/curbside events
- Micromobility (bike/scooter) availability + rebalancing

### Output principali
- Dashboard real-time (aggregazioni spazio-temporali)
- Alerting (anomalie e soglie)
- Input per ottimizzazione/routing

## 3) Flotte droni (UAV) e robotics

### Fonti target
- Telemetria flotta (posizione, batteria, mission status)
- Eventi missione (takeoff/landing, waypoint, failure)
- Artifact edge (immagini/video metadata, detection)

### Requisiti
- Time series ad alta frequenza + indicizzazione geospaziale
- Provenance/audit (mission_id, operator, firmware)
- Tiering storage e retention

## 4) Real-time + agentic operations (Feeless pools)

Obiettivo: usare segnali streaming per alimentare agenti (risk/allocation/scheduling) e feature near-real-time, con backfill batch dove serve.

## 5) Piano di validazione (quando diventa esempio)

Ogni esempio dovrebbe includere:
- schema canonico
- pattern ingestion (stream → storage durabile)
- query layer (Trino/SQL)
- osservabilità + cost attribution
- un “decision loop” minimo (alert o input agentico)


