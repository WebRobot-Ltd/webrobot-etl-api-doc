---
title: Partner tecnici
version: 1.0.0
description: "Come creare estensioni personalizzate: plugin Jersey (API) e plugin ETL (stages/resolvers/actions), e quando usare Python Extensions"
---

# Partner tecnici

Questa sezione è per **admin** e **partner tecnici** che vogliono estendere WebRobot in modo **supportato**.

Esistono 3 meccanismi principali di estensione:

- **Plugin Jersey (API)**: aggiungono endpoint REST nel backend (es. EAN plugin). Richiedono compilazione e deployment di JAR.
- **Plugin ETL (Spark/ETL runtime)**: aggiungono stage/resolver/actions usabili nelle pipeline YAML (es. `example-plugin`). Richiedono compilazione e deployment di JAR.
- **Python Extensions**: meccanismo chiave per **auto-programmazione agentica** di stage personalizzati **senza compilazione**. Riservato ad admin e partner tecnici. Presupposto fondamentale per massima estendibilità richiesta dalla natura agentica di WebRobot.

---

## 1) Plugin Jersey (API) – stile EAN

### Cos’è
Un plugin Jersey è una risorsa JAX-RS (`@Path`) caricata:
- **staticamente** dal classpath (core plugins),
- oppure **dinamicamente** da MinIO/database tramite `PluginManager` (client plugins).

### Struttura minima
- una o più classi `@Path("/webrobot/api/<nome-plugin>")`
- eventuale bootstrap (`@PostConstruct`) per creare risorse (Project/Agent/Job) e inizializzare configurazioni
- se servono upload: `@Consumes(MediaType.MULTIPART_FORM_DATA)` (MultiPartFeature è già registrato)

### Pattern consigliato (come EAN)
- **Bootstrap**: crea/aggiorna `Organization` + `Project` + `Agent(pipelineYaml)` + `Job template`.
- **Endpoint** “semplificati”: `upload`, `execute`, `schedule`, `status`, ecc.
- **Pipeline YAML**: salvata su `Agent.pipelineYaml`; prima dell’esecuzione viene rigenerato `pysparkCode` per avere sempre l’ultima logica.
- **Cloud credentials**: passabili via request (`cloudCredentialIds`) oppure auto-discovery per provider; poi vengono iniettate in env del job Spark.

Vedi anche: guida [EAN Image Sourcing Plugin](ean-image-sourcing.md).

---

## 2) Plugin ETL (Spark) – stile `example-plugin`

### Cos’è
Un plugin ETL aggiunge componenti al runtime ETL:
- **Pipeline stages** (`PipelineStage`) invocabili da YAML (`stage: ...`)
- **Attribute resolvers** (`AttributeResolver`) usabili in `extract`/`flatSelect` (`method: ...`)
- **Action factories** (azioni in `fetch.traces`)

### Stage plugin: requisiti
Uno stage è una classe che implementa `PipelineStage` e definisce `stageName`, poi viene registrata in `StageRegistry`.

Nel `example-plugin` la registrazione avviene centralmente in `Plugin.registerAll()` (stage + alias).

### Come viene “caricato” lo stage
Il runtime Spark può caricare plugin ETL in 2 modi:
- **Jar plugin** registrato nel job Spark (manuale / da DB) e poi `StageRegistry.register(...)`.
- **Stage già incluso** nel classpath dell’immagine Spark (core).

Per i partner: la modalità più comune è fornire un **JAR** (plugin ETL) e renderlo disponibile al job (DB/MinIO), così gli stage diventano usabili nella pipeline YAML.

### Checklist per uno stage nuovo
- Definire `stageName` stabile (e opzionali alias snake_case)
- Documentare `args` e default
- Validare con esempi YAML reali

---

## 3) Python Extensions (meccanismo chiave per auto-programmazione agentica)

### Natura agentica e massima estendibilità

La **natura agentica** di WebRobot richiede **massimo livello di estendibilità** delle pipeline. Le **Python Extensions** sono il **presupposto fondamentale** per l'auto-programmazione di stage personalizzati da parte di AI agents, **senza la necessità di compilare plugin specifici**.

### Caratteristiche chiave

- **No compilation required**: Le Python extensions vengono caricate dinamicamente a runtime, senza necessità di compilare e distribuire plugin JAR
- **Auto-programmazione agentica**: Meccanismo ideale per AI agents che generano dinamicamente trasformazioni, resolver e stage personalizzati
- **Accesso riservato**: Funzionalità riservata a **admin** e **partner tecnici** per garantire sicurezza e controllo
- **Massima flessibilità**: Permette iterazione rapida e adattamento dinamico delle pipeline senza deployment di nuove versioni

### Quando usarle

Le Python extensions sono indicate quando:
- uno strato "AI agent" genera **dinamicamente** trasformazioni/resolver/stage in Python
- vuoi iterare rapidamente senza pubblicare un nuovo JAR
- necessiti di massima estendibilità per pipeline agentiche che si adattano dinamicamente

### Endpoint dedicato (inline YAML mode)

È disponibile un endpoint dedicato per processare YAML e generare/aggiornare codice PySpark dell'Agent:

- `POST /webrobot/api/python-extensions/process-yaml`

**Autenticazione**: Richiede API key con privilegi di **admin** o **partner tecnico**.

Payload tipico:
- `agentId`
- `yamlContent` (pipeline YAML + eventuale sezione `python_extensions` per codegen)

Nota: alcune API "DB-based" per estensioni possono risultare non attive a runtime (dipende dalla build); il flusso stabile oggi è **process-yaml** (inline).


