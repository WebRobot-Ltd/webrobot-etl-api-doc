# Modalità Docs Multipagina con Docker

Questo documento spiega come utilizzare la modalità docs multipagina anche in Docker, senza dover usare Redocly Realm cloud.

## Due approcci disponibili

### 1. Dockerfile standard (modalità API-only)
Il `Dockerfile` standard genera un file HTML statico usando `redocly build-docs`. Questo approccio:
- ✅ Genera file statico leggero
- ✅ Usa nginx per servire file statici
- ❌ Non supporta modalità docs multipagina
- ❌ Solo documentazione API OpenAPI

**Uso:**
```bash
docker build -t webrobot-etl-api-doc .
```

### 2. Dockerfile.docs (modalità docs multipagina)
Il `Dockerfile.docs` serve `redocly preview` in produzione usando nginx come reverse proxy. Questo approccio:
- ✅ Supporta modalità docs multipagina completa
- ✅ Include sidebar navigation
- ✅ Supporta guide Markdown
- ✅ Compatibile con deployment Kubernetes esistente
- ⚠️ Richiede più risorse (Node.js + nginx)
- ⚠️ Non è un build statico puro

**Uso:**
```bash
docker build -f Dockerfile.docs -t webrobot-etl-api-doc:docs .
```

## Configurazione Kubernetes

Per usare la versione docs, aggiorna il deployment:

```yaml
containers:
- name: api-doc
  image: ghcr.io/webrobot-ltd/webrobot-etl-api-doc:docs  # Usa tag :docs
  ports:
  - containerPort: 80  # Stessa porta, nginx fa da proxy
```

Le risorse consigliate per la modalità docs:
```yaml
resources:
  requests:
    memory: "128Mi"  # Aumentato da 64Mi
    cpu: "100m"      # Aumentato da 50m
  limits:
    memory: "256Mi"  # Aumentato da 128Mi
    cpu: "200m"      # Aumentato da 100m
```

## Build e test locale

```bash
# Build immagine docs
docker build -f Dockerfile.docs -t webrobot-etl-api-doc:docs .

# Test locale
docker run -p 8080:80 webrobot-etl-api-doc:docs

# Accedi a http://localhost:8080
```

## Vantaggi della modalità docs

- **Multipagina**: Guide separate, non solo API reference
- **Sidebar navigation**: Navigazione facile tra sezioni
- **Markdown support**: Guide scritte in Markdown
- **Stessa configurazione**: Usa `.redocly.yaml` e `sidebars.yaml`

## Note

- La modalità docs richiede Node.js in esecuzione (non è un build statico puro)
- Il preview server di Redocly gestisce il rendering in tempo reale
- Nginx fa da reverse proxy per servire sulla porta 80 standard
- Supervisor gestisce entrambi i processi (nginx + redocly preview)

