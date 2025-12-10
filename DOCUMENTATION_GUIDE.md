# Guida per Arricchire la Documentazione API

Questa guida spiega come aggiungere descrizioni dettagliate, esempi e informazioni utili agli endpoint OpenAPI.

## Struttura di un Endpoint Arricchito

Ogni operazione dovrebbe includere:

1. **`summary`**: Breve descrizione (max 120 caratteri)
2. **`description`**: Descrizione dettagliata con markdown
3. **`tags`**: Categorie per organizzare gli endpoint
4. **`parameters`**: Descrizioni per ogni parametro
5. **`requestBody`**: Esempi e descrizioni
6. **`responses`**: Codici di risposta dettagliati con esempi

## Esempio Completo

```yaml
/webrobot/api/projects/id/{projectId}/jobs/{jobId}/execute:
  post:
    tags:
      - Jobs
      - ETL Execution
    summary: Esegue un job Spark immediatamente
    description: |
      Esegue un job Spark in modalità immediata, allocando risorse nel cluster Kubernetes.
      
      Il job viene eseguito con le configurazioni specificate nel job stesso o tramite
      parametri opzionali nella richiesta.
      
      **Note importanti:**
      - Il job deve essere associato a un Agent con codice PySpark valido
      - Le credenziali cloud vengono iniettate automaticamente se configurate
      - Il webhook viene chiamato automaticamente all'inizio (RUNNING) e alla fine (COMPLETED/FAILED)
      
      **Rate Limiting:** Max 10 esecuzioni simultanee per progetto
    operationId: executeJob
    parameters:
      - name: projectId
        in: path
        required: true
        description: ID univoco del progetto
        schema:
          type: string
          example: "98"
      - name: jobId
        in: path
        required: true
        description: ID univoco del job da eseguire
        schema:
          type: string
          example: "210"
    requestBody:
      required: false
      description: |
        Parametri opzionali per l'esecuzione del job.
        
        Se non specificati, vengono usati i valori di default del job.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/JobExecutionRequest'
          examples:
            default:
              summary: Esecuzione con parametri di default
              value: {}
            withCredentials:
              summary: Esecuzione con credenziali cloud specifiche
              value:
                cloudCredentialIds:
                  - "550e8400-e29b-41d4-a716-446655440000"
    responses:
      '200':
        description: Job eseguito con successo
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/JobExecutionResponse'
            example:
              executionId: "spark-2d53940045a6-95379617"
              status: "SUBMITTED"
              message: "Job execution submitted successfully"
              clusterId: "default-cluster"
              success: true
      '400':
        description: Richiesta non valida
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Error'
            example:
              error: "Job not found or invalid configuration"
              code: 400
      '401':
        description: Non autorizzato - API key mancante o non valida
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Error'
      '403':
        description: Permessi insufficienti - scope `etl:execute` richiesto
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Error'
      '404':
        description: Progetto o job non trovato
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Error'
      '409':
        description: Job già in esecuzione
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Error'
            example:
              error: "Job already running"
              code: 409
      '500':
        description: Errore interno del server
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Error'
```

## Categorie di Endpoint (Tags)

Organizza gli endpoint con questi tag:

- **Projects**: Gestione progetti
- **Jobs**: Gestione job ETL
- **Tasks**: Gestione task
- **Agents**: Gestione agenti PySpark
- **Datasets**: Gestione dataset
- **EAN Plugin**: Plugin EAN Image Sourcing
- **Cloud**: Operazioni cloud (Spark, Scheduler)
- **Health**: Health check e status

## Best Practices

1. **Summary**: Sii conciso ma descrittivo
2. **Description**: Usa markdown per formattare (liste, codice, grassetto)
3. **Examples**: Fornisci sempre esempi pratici
4. **Error Responses**: Documenta tutti i possibili errori
5. **Parameters**: Spiega cosa fa ogni parametro e quando è obbligatorio
6. **Rate Limiting**: Documenta limiti di rate se applicabili

## Script per Aggiornare la Documentazione

Usa lo script `scripts/enrich-documentation.sh` per aggiungere automaticamente descrizioni base agli endpoint che ne sono privi.

