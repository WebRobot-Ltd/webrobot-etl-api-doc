#!/bin/bash

# Script per aggiornare la specifica OpenAPI dall'API in esecuzione

set -e

API_URL="${API_URL:-https://api.webrobot.eu/api}"
OUTPUT_FILE="${OUTPUT_FILE:-openapi.yaml}"

echo "🚀 Aggiornamento specifica OpenAPI da ${API_URL}"

# Verifica che l'API sia raggiungibile
if ! curl -s -f "${API_URL}/api/health" > /dev/null 2>&1; then
    echo "❌ Errore: API non raggiungibile su ${API_URL}"
    echo "   Assicurati che l'API sia in esecuzione o imposta la variabile API_URL"
    exit 1
fi

echo "✅ API raggiungibile"

# Estrai OpenAPI JSON
echo "📥 Estrazione specifica OpenAPI..."
OPENAPI_JSON=$(curl -s "${API_URL}/api/openapi.json")

if [ -z "$OPENAPI_JSON" ] || [ "$OPENAPI_JSON" == "null" ]; then
    echo "❌ Errore: Impossibile ottenere la specifica OpenAPI"
    exit 1
fi

# Converti JSON a YAML usando js-yaml (se disponibile) o python
if command -v js-yaml &> /dev/null; then
    echo "$OPENAPI_JSON" | js-yaml > "$OUTPUT_FILE"
elif command -v python3 &> /dev/null; then
    echo "$OPENAPI_JSON" | python3 -c "
import json, sys, yaml
try:
    data = json.load(sys.stdin)
    print(yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False))
except ImportError:
    print('Errore: pyyaml non installato. Installa con: pip install pyyaml', file=sys.stderr)
    sys.exit(1)
" > "$OUTPUT_FILE"
else
    echo "❌ Errore: js-yaml o python3 con pyyaml richiesti per la conversione"
    echo "   Installa con: npm install -g js-yaml"
    echo "   Oppure: pip install pyyaml"
    exit 1
fi

echo "✅ Specifica OpenAPI aggiornata in ${OUTPUT_FILE}"

# Valida con Redocly (se disponibile)
if command -v redocly &> /dev/null; then
    echo "🔍 Validazione con Redocly..."
    redocly lint "$OUTPUT_FILE" || echo "⚠️  Avvisi di validazione trovati"
fi

echo "✨ Completato!"

