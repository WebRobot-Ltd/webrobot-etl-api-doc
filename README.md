# WebRobot ETL API Documentation

Documentazione API generata con [Redocly](https://redocly.com/) e [Redoc](https://github.com/Redocly/redoc).

## Setup

### Installazione Redocly CLI

```bash
npm install -g @redocly/cli
```

### Sviluppo Locale

Per visualizzare la documentazione in locale:

```bash
# Avvia il server di sviluppo
redocly preview-docs

# Oppure con Redoc standalone
npx redoc-cli serve openapi.yaml --port 8080
```

### Build

Per generare la documentazione statica:

```bash
# Build con Redocly
redocly build-docs

# Oppure con Redoc standalone
npx redoc-cli bundle openapi.yaml -o dist/index.html
```

## Aggiornamento OpenAPI Spec

La specifica OpenAPI può essere estratta dall'API in esecuzione:

```bash
# Dall'API locale
curl http://localhost:8020/api/openapi.json > openapi.json

# Dall'API di produzione
curl https://api.webrobot.eu/api/openapi.json > openapi.json

# Converti JSON a YAML (se necessario)
npx js-yaml openapi.json > openapi.yaml
```

## Struttura

- `openapi.yaml` - Specifica OpenAPI principale
- `redocly.yaml` - Configurazione Redocly
- `decorators/` - Decoratori personalizzati (opzionale)
- `dist/` - Output della build (generato)

## Deployment

La documentazione può essere deployata su:

- **GitHub Pages**: Abilita GitHub Pages nel repository
- **Netlify**: Connetto il repository a Netlify
- **Vercel**: Connetto il repository a Vercel
- **Redocly Cloud**: Usa Redocly Cloud per hosting gratuito

## Riferimenti

- [Redocly Documentation](https://redocly.com/docs/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Redoc GitHub](https://github.com/Redocly/redoc)

