#!/usr/bin/env python3
"""
Script per arricchire automaticamente tutti gli endpoint OpenAPI rimanenti
con descrizioni standardizzate basate sui pattern degli endpoint.
"""

import yaml
import re
from pathlib import Path

def get_endpoint_info(path, method):
    """Genera informazioni standardizzate per un endpoint basandosi sul path e metodo."""
    path_lower = path.lower()
    method_upper = method.upper()
    
    # Determina tags
    tags = []
    if '/projects/' in path_lower:
        tags.append('Projects')
    if '/jobs/' in path_lower:
        tags.append('Jobs')
    if '/tasks/' in path_lower:
        tags.append('Tasks')
    if '/agents/' in path_lower:
        tags.append('Agents')
    if '/datasets' in path_lower:
        tags.append('Datasets')
    if '/categories/' in path_lower:
        tags.append('Categories')
    if '/cloud-credentials' in path_lower:
        tags.append('Cloud Credentials')
    if '/admin/' in path_lower:
        tags.append('Admin')
    if '/package/' in path_lower:
        tags.append('Package')
    if '/python-extensions' in path_lower:
        tags.append('Python Extensions')
    if '/ai-providers' in path_lower:
        tags.append('AI Providers')
    if '/ean-image-sourcing' in path_lower:
        tags.append('EAN Plugin')
    
    # Genera summary e description basati sul metodo e path
    if method_upper == 'GET':
        if '/id/' in path_lower or '/{id}' in path_lower or '/{name}' in path_lower:
            summary = f"Ottiene una risorsa specifica"
            description = f"Restituisce i dettagli di una risorsa specifica identificata dall'ID o nome nel path."
        elif 'all' in path_lower or path.endswith('s') and not path.endswith('{id}'):
            summary = f"Ottiene tutte le risorse"
            description = f"Restituisce la lista di tutte le risorse disponibili nel sistema."
        elif '/status' in path_lower:
            summary = f"Ottiene lo status di una risorsa"
            description = f"Restituisce lo stato attuale di una risorsa, incluse informazioni su esecuzione e progresso."
        elif '/logs' in path_lower:
            summary = f"Ottiene i log di una risorsa"
            description = f"Restituisce i log di esecuzione di una risorsa."
        elif '/info' in path_lower:
            summary = f"Ottiene informazioni su una risorsa"
            description = f"Restituisce informazioni generali su una risorsa, incluse versioni e configurazioni."
        elif '/health' in path_lower:
            summary = f"Health check"
            description = f"Verifica lo stato di salute di un servizio o risorsa."
        else:
            summary = f"Ottiene dati"
            description = f"Restituisce dati relativi alla risorsa specificata."
    elif method_upper == 'POST':
        if '/execute' in path_lower:
            summary = f"Esegue un'operazione"
            description = f"Esegue un'operazione o avvia un processo per la risorsa specificata."
        elif '/upload' in path_lower:
            summary = f"Carica un file o dataset"
            description = f"Carica un file o dataset nel sistema."
        elif '/schedule' in path_lower:
            summary = f"Schedula un'operazione"
            description = f"Crea o aggiorna la schedulazione di un'operazione ricorrente."
        else:
            summary = f"Crea una nuova risorsa"
            description = f"Crea una nuova risorsa nel sistema con i dati forniti nella richiesta."
    elif method_upper == 'PUT':
        summary = f"Aggiorna una risorsa"
        description = f"Aggiorna i dati di una risorsa esistente con i nuovi valori forniti."
    elif method_upper == 'DELETE':
        summary = f"Elimina una risorsa"
        description = f"Elimina una risorsa dal sistema. **Attenzione:** Questa operazione è irreversibile."
    elif method_upper == 'PATCH':
        summary = f"Modifica parziale di una risorsa"
        description = f"Applica una modifica parziale a una risorsa esistente."
    else:
        summary = f"Operazione {method_upper}"
        description = f"Esegue un'operazione {method_upper} sulla risorsa specificata."
    
    return {
        'tags': tags if tags else ['API'],
        'summary': summary,
        'description': description
    }

def enrich_parameter(param):
    """Arricchisce un parametro con descrizione se mancante."""
    if 'description' not in param:
        param_name = param.get('name', '')
        if 'Id' in param_name:
            resource = param_name.replace('Id', '').lower()
            param['description'] = f"ID univoco del {resource if resource else 'elemento'}"
        elif param_name == 'name':
            param['description'] = "Nome della risorsa"
        elif param_name == 'namespace':
            param['description'] = "Namespace Kubernetes (opzionale)"
        elif param_name == 'provider':
            param['description'] = "Nome del provider (es. 'aws', 'azure', 'gcp')"
        elif param_name == 'country':
            param['description'] = "Codice paese ISO (es. 'denmark', 'italy', 'france')"
        elif param_name == 'page':
            param['description'] = "Numero di pagina (0-based)"
        elif param_name == 'pageSize':
            param['description'] = "Dimensione della pagina"
        elif param_name == 'status':
            param['description'] = "Filtra per status"
        elif param_name == 'offset':
            param['description'] = "Offset per la paginazione"
        elif param_name == 'limit':
            param['description'] = "Numero massimo di risultati"
    return param

def enrich_responses(operation, method):
    """Arricchisce le responses con codici HTTP standard."""
    if 'responses' not in operation:
        operation['responses'] = {}
    
    responses = operation['responses']
    
    # Se c'è solo 'default', sostituiscilo con codici standard
    if 'default' in responses and len(responses) == 1:
        default_resp = responses.pop('default')
        content = default_resp.get('content', {'application/json': {}})
        
        if method.upper() == 'GET':
            responses['200'] = {
                'description': 'Operazione completata con successo',
                'content': content
            }
            responses['404'] = {
                'description': 'Risorsa non trovata',
                'content': {
                    'application/json': {
                        'schema': {'$ref': '#/components/schemas/Error'}
                    }
                }
            }
        elif method.upper() == 'POST':
            responses['201'] = {
                'description': 'Risorsa creata con successo',
                'content': content
            }
            responses['400'] = {
                'description': 'Richiesta non valida',
                'content': {
                    'application/json': {
                        'schema': {'$ref': '#/components/schemas/Error'}
                    }
                }
            }
        elif method.upper() == 'PUT':
            responses['200'] = {
                'description': 'Risorsa aggiornata con successo',
                'content': content
            }
            responses['400'] = {
                'description': 'Richiesta non valida',
                'content': {
                    'application/json': {
                        'schema': {'$ref': '#/components/schemas/Error'}
                    }
                }
            }
        elif method.upper() == 'DELETE':
            responses['200'] = {
                'description': 'Risorsa eliminata con successo',
                'content': content
            }
            responses['404'] = {
                'description': 'Risorsa non trovata',
                'content': {
                    'application/json': {
                        'schema': {'$ref': '#/components/schemas/Error'}
                    }
                }
            }
    
    # Aggiungi sempre errori comuni se non presenti
    if '401' not in responses:
        responses['401'] = {
            'description': 'Non autorizzato',
            'content': {
                'application/json': {
                    'schema': {'$ref': '#/components/schemas/Error'}
                }
            }
        }
    if '500' not in responses:
        responses['500'] = {
            'description': 'Errore interno del server',
            'content': {
                'application/json': {
                    'schema': {'$ref': '#/components/schemas/Error'}
                }
            }
        }

def main():
    openapi_file = Path(__file__).parent.parent / 'openapi.yaml'
    
    print(f"📖 Leggendo {openapi_file}...")
    with open(openapi_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    paths = data.get('paths', {})
    enriched_count = 0
    
    print(f"🔍 Trovati {len(paths)} path...")
    
    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if method in ['get', 'post', 'put', 'delete', 'patch'] and 'operationId' in operation:
                # Arricchisci solo se manca summary o description
                if 'summary' not in operation or 'description' not in operation:
                    info = get_endpoint_info(path, method)
                    
                    if 'summary' not in operation:
                        operation['summary'] = info['summary']
                    if 'description' not in operation:
                        operation['description'] = info['description']
                    if 'tags' not in operation:
                        operation['tags'] = info['tags']
                    
                    # Arricchisci parametri
                    if 'parameters' in operation:
                        operation['parameters'] = [enrich_parameter(p) for p in operation['parameters']]
                    
                    # Arricchisci responses
                    enrich_responses(operation, method)
                    
                    enriched_count += 1
    
    print(f"✨ Arricchiti {enriched_count} endpoint...")
    
    # Salva
    print(f"💾 Salvando in {openapi_file}...")
    with open(openapi_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
    
    print("✅ Completato!")

if __name__ == '__main__':
    main()

