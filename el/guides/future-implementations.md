---
title: Μελλοντικές υλοποιήσεις (Roadmap) (EL)
version: 1.0.0
description: "Μελλοντικές κατευθύνσεις: streaming ingestion (IoT), smart city & mobility, στόλοι drones, real-time agentic operations"
---

# Μελλοντικές υλοποιήσεις (Roadmap) (EL)

Αυτή η σελίδα συνοψίζει **μελλοντικές** κατευθύνσεις για το WebRobot σε domains που απαιτούν **streaming ingestion**, **real-time analytics** και **operational decision loops**.

> Σημείωση: πρόκειται για αρχιτεκτονικό/roadmap έγγραφο. Αποφεύγει σκόπιμα λεπτομέρειες υλοποίησης του core engine.

## 1) Streaming sources (IoT)

### Πηγές
- MQTT brokers (sensors, meters, building automation)
- Kafka/Pulsar topics (event buses)
- AMQP/RabbitMQ (legacy)
- Webhooks / HTTP collectors (device gateways)

### Canonical model (concept)
- **event_time** vs **ingest_time**
- **device_id / asset_id**
- **geo** (lat/lon + optional geohash)
- **telemetry payload** (typed metrics + raw JSON)
- **provenance**: source, tenant, schema version

### Key capabilities
- Schema validation + evolution (Schema Registry model)
- Late/out-of-order events (watermarks)
- Dedup by `(device_id, event_time, sequence_id)`
- Quality checks (gaps, outliers, drift)

## 2) Smart city & mobility

### Use cases
- Traffic/congestion monitoring
- Public transport analytics (e.g., GTFS-RT)
- Parking/curbside events
- Micromobility availability & rebalancing signals

### Outputs
- Real-time dashboards (spatio-temporal aggregates)
- Alerting (anomalies/thresholds)
- Optimization inputs (routing/incidents)

## 3) Drone fleets (UAV) & robotics

### Sources
- Fleet telemetry (position, battery, mission status)
- Mission events (takeoff/landing, waypoint, failures)
- Edge artifacts (images/video metadata, detections)

### Requirements
- High-frequency time series + geospatial indexing
- Provenance/audit (mission_id, operator, firmware)
- Storage tiering + retention

## 4) Real-time + agentic operations (Feeless pools)

Στόχος: streaming signals → agentic tools (risk/allocation/scheduling) + near-real-time features, με batch backfills όπου χρειάζεται.

## 5) Validation plan (when implemented as examples)

Κάθε μελλοντικό παράδειγμα θα πρέπει να περιλαμβάνει:
- canonical schema
- ingestion pattern (stream → durable storage)
- query layer (Trino/SQL)
- observability + cost attribution
- minimal decision loop (alert or agent input)


