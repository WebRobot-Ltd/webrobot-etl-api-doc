#!/usr/bin/env python3
"""
Script per arricchire automaticamente gli endpoint OpenAPI con descrizioni standardizzate.
Questo script aggiunge summary, description, tags e responses dettagliati agli endpoint che ne sono privi.
"""

import yaml
import re
from pathlib import Path

# Mappatura endpoint -> descrizioni
ENDPOINT_DESCRIPTIONS = {
    # EAN Plugin
    '/webrobot/api/ean-image-sourcing/{country}/execute': {
        'summary': 'Esegue un job EAN Image Sourcing per un paese',
        'description': 'Esegue un job Spark per il sourcing di immagini EAN per il paese specificato.',
        'tags': ['EAN Plugin', 'Jobs'],
    },
    '/webrobot/api/ean-image-sourcing/bootstrap/status': {
        'summary': 'Ottiene lo status del bootstrap EAN',
        'description': 'Verifica lo status del processo di bootstrap per il plugin EAN Image Sourcing.',
        'tags': ['EAN Plugin', 'Bootstrap'],
    },
    '/webrobot/api/ean-image-sourcing/info': {
        'summary': 'Ottiene informazioni sul plugin EAN',
        'description': 'Restituisce informazioni sul plugin EAN Image Sourcing, incluse versione e configurazioni.',
        'tags': ['EAN Plugin', 'Info'],
    },
    '/webrobot/api/ean-image-sourcing/{country}/query': {
        'summary': 'Esegue una query sul dataset EAN',
        'description': 'Esegue una query personalizzata sul dataset EAN del paese specificato.',
        'tags': ['EAN Plugin', 'Query'],
    },
    '/webrobot/api/ean-image-sourcing/{country}/schedule': {
        'summary': 'Schedula un job EAN ricorrente',
        'description': 'Crea o aggiorna la schedulazione di un job EAN Image Sourcing ricorrente per un paese.',
        'tags': ['EAN Plugin', 'Scheduler'],
    },
    '/webrobot/api/ean-image-sourcing/{country}/upload': {
        'summary': 'Carica un dataset EAN',
        'description': 'Carica un nuovo dataset EAN per il paese specificato.',
        'tags': ['EAN Plugin', 'Upload'],
    },
}

def enrich_endpoint(path, method, operation):
    """Arricchisce un singolo endpoint con descrizioni standardizzate."""
    endpoint_path = path
    
    # Cerca descrizione personalizzata
    if endpoint_path in ENDPOINT_DESCRIPTIONS:
        desc = ENDPOINT_DESCRIPTIONS[endpoint_path]
        if 'summary' not in operation:
            operation['summary'] = desc['summary']
        if 'description' not in operation:
            operation['description'] = desc['description']
        if 'tags' not in operation:
            operation['tags'] = desc['tags']
    
    # Aggiungi tags generici basati sul path
    if 'tags' not in operation:
        tags = []
        if '/projects/' in endpoint_path:
            tags.append('Projects')
        if '/jobs/' in endpoint_path:
            tags.append('Jobs')
        if '/tasks/' in endpoint_path:
            tags.append('Tasks')
        if '/agents/' in endpoint_path:
            tags.append('Agents')
        if '/datasets/' in endpoint_path:
            tags.append('Datasets')
        if '/categories/' in endpoint_path:
            tags.append('Categories')
        if '/cloud/' in endpoint_path:
            tags.append('Cloud')
        if '/admin/' in endpoint_path:
            tags.append('Admin')
        if tags:
            operation['tags'] = tags
    
    # Migliora responses
    if 'responses' in operation:
        if 'default' in operation['responses']:
            # Sostituisci default con codici HTTP standard
            default_resp = operation['responses'].pop('default')
            if method.upper() == 'GET':
                operation['responses']['200'] = {
                    'description': 'Operazione completata con successo',
                    'content': default_resp.get('content', {'application/json': {}})
                }
                operation['responses']['404'] = {
                    'description': 'Risorsa non trovata',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Error'}
                        }
                    }
                }
            elif method.upper() == 'POST':
                operation['responses']['201'] = {
                    'description': 'Risorsa creata con successo',
                    'content': default_resp.get('content', {'application/json': {}})
                }
                operation['responses']['400'] = {
                    'description': 'Richiesta non valida',
                    'content': {
                        'application/json': {
                            'schema': {'$ref': '#/components/schemas/Error'}
                        }
                    }
                }
            elif method.upper() == 'PUT':
                operation['responses']['200'] = {
                    'description': 'Risorsa aggiornata con successo',
                    'content': default_resp.get('content', {'application/json': {}})
                }
            elif method.upper() == 'DELETE':
                operation['responses']['200'] = {
                    'description': 'Risorsa eliminata con successo',
                    'content': default_resp.get('content', {'application/json': {}})
                }
            
            # Aggiungi sempre errori comuni
            operation['responses']['401'] = {
                'description': 'Non autorizzato',
                'content': {
                    'application/json': {
                        'schema': {'$ref': '#/components/schemas/Error'}
                    }
                }
            }
            operation['responses']['500'] = {
                'description': 'Errore interno del server',
                'content': {
                    'application/json': {
                        'schema': {'$ref': '#/components/schemas/Error'}
                    }
                }
            }
    
    # Migliora parametri
    if 'parameters' in operation:
        for param in operation['parameters']:
            if 'description' not in param:
                param_name = param.get('name', '')
                if param_name in ['projectId', 'jobId', 'taskId', 'agentId', 'datasetId', 'categoryId']:
                    param['description'] = f'ID univoco del {param_name.replace("Id", "")}'
                elif param_name == 'country':
                    param['description'] = 'Codice paese ISO (es. "denmark", "italy", "france")'
                elif param_name == 'namespace':
                    param['description'] = 'Namespace Kubernetes (opzionale)'
    
    return operation

def main():
    openapi_file = Path(__file__).parent.parent / 'openapi.yaml'
    
    print(f"📖 Leggendo {openapi_file}...")
    with open(openapi_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    paths = data.get('paths', {})
    enriched_count = 0
    
    print(f"🔍 Trovati {len(paths)} endpoint...")
    
    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                if 'operationId' in operation:
                    # Arricchisci solo se manca summary o description
                    if 'summary' not in operation or 'description' not in operation:
                        enrich_endpoint(path, method, operation)
                        enriched_count += 1
    
    print(f"✨ Arricchiti {enriched_count} endpoint...")
    
    # Salva
    print(f"💾 Salvando in {openapi_file}...")
    with open(openapi_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print("✅ Completato!")

if __name__ == '__main__':
    main()

