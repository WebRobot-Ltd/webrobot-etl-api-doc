# Build a Pipeline

This guide walks you through creating a CI/CD pipeline using the WebRobot ETL API. You'll learn how to define stages, configure parameters, and generate Jenkins YAML automatically.

## Overview

A pipeline consists of:
- **Stages**: Sequential steps in your CI/CD process
- **Parameters**: User-configurable build options
- **Environment Variables**: Configuration values shared across stages
- **Input/Output**: Data flow between stages

## Step 1: Create a Pipeline

First, create a new pipeline configuration:

```bash
curl -X POST https://api.webrobot.eu/api/webrobot/api/pipelines \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "your-project-id",
    "name": "my-pipeline",
    "description": "My first CI/CD pipeline",
    "repositoryUrl": "https://github.com/your-org/your-repo",
    "dockerImage": "ghcr.io/your-org/your-app",
    "k8sNamespace": "webrobot",
    "k8sContext": "webrobot",
    "enabled": true
  }'
```

**Response:**
```json
{
  "id": 1,
  "projectId": "your-project-id",
  "name": "my-pipeline",
  "description": "My first CI/CD pipeline",
  "repositoryUrl": "https://github.com/your-org/your-repo",
  "dockerImage": "ghcr.io/your-org/your-app",
  "k8sNamespace": "webrobot",
  "k8sContext": "webrobot",
  "enabled": true,
  "createdAt": "2025-12-12T10:00:00Z"
}
```

Save the `id` from the response - you'll need it for the next steps.

## Step 2: Add Parameters

Define build parameters that users can configure:

```bash
curl -X POST https://api.webrobot.eu/api/webrobot/api/pipelines/1/parameters \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "name": "BUILD_TYPE",
      "type": "choice",
      "choices": ["dev", "staging", "production"],
      "defaultValue": "dev",
      "description": "Build environment type"
    },
    {
      "name": "PUSH_IMAGE",
      "type": "boolean",
      "defaultValue": true,
      "description": "Push Docker image to registry"
    },
    {
      "name": "DEPLOY_K8S",
      "type": "boolean",
      "defaultValue": true,
      "description": "Deploy to Kubernetes"
    }
  ]'
```

## Step 3: Configure Environment Variables

Set environment variables available to all stages:

```bash
curl -X POST https://api.webrobot.eu/api/webrobot/api/pipelines/1/environment \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "key": "GITHUB_REPOSITORY",
      "value": "your-org/your-repo"
    },
    {
      "key": "DOCKER_IMAGE",
      "value": "ghcr.io/${GITHUB_REPOSITORY}"
    },
    {
      "key": "K8S_NAMESPACE",
      "value": "webrobot"
    }
  ]'
```

## Step 4: Add Stages

### Stage 1: Initialize

```bash
curl -X POST https://api.webrobot.eu/api/webrobot/api/pipelines/1/stages \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Initialize",
    "order": 1,
    "type": "script",
    "description": "Initialize build environment",
    "agent": {
      "type": "any"
    },
    "steps": [
      {
        "type": "script",
        "script": "env.DO_DEPLOY = false"
      }
    ],
    "inputs": [],
    "outputs": [
      {
        "name": "DO_DEPLOY",
        "type": "boolean",
        "description": "Flag to enable automatic deployment"
      }
    ]
  }'
```

### Stage 2: Checkout

```bash
curl -X POST https://api.webrobot.eu/api/webrobot/api/pipelines/1/stages \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Checkout",
    "order": 2,
    "type": "checkout",
    "description": "Checkout source code from repository",
    "agent": {
      "type": "any"
    },
    "steps": [
      {
        "type": "checkout",
        "scm": "git"
      }
    ],
    "inputs": [],
    "outputs": [
      {
        "name": "WORKSPACE",
        "type": "string",
        "description": "Workspace directory path"
      }
    ]
  }'
```

### Stage 3: Build

```bash
curl -X POST https://api.webrobot.eu/api/webrobot/api/pipelines/1/stages \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Build",
    "order": 3,
    "type": "build",
    "description": "Build application",
    "when": {
      "condition": "!params.REDEPLOY_ONLY"
    },
    "agent": {
      "type": "kubernetes",
      "label": "nodejs",
      "yaml": "apiVersion: v1\nkind: Pod\nspec:\n  containers:\n  - name: nodejs\n    image: node:18-alpine"
    },
    "steps": [
      {
        "type": "script",
        "script": "npm ci"
      },
      {
        "type": "script",
        "script": "npm run build"
      }
    ],
    "inputs": [
      {
        "name": "WORKSPACE",
        "type": "string",
        "required": true
      }
    ],
    "outputs": [
      {
        "name": "BUILD_ARTIFACT",
        "type": "string",
        "description": "Path to build artifact"
      }
    ]
  }'
```

### Stage 4: Build & Push Docker Image

```bash
curl -X POST https://api.webrobot.eu/api/webrobot/api/pipelines/1/stages \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Build & Push Docker Image",
    "order": 4,
    "type": "docker",
    "description": "Build and push Docker image",
    "when": {
      "condition": "!params.REDEPLOY_ONLY && params.PUSH_IMAGE"
    },
    "agent": {
      "type": "kubernetes",
      "label": "docker",
      "yaml": "apiVersion: v1\nkind: Pod\nspec:\n  containers:\n  - name: kaniko\n    image: gcr.io/kaniko-project/executor:v1.9.0"
    },
    "steps": [
      {
        "type": "script",
        "script": "/kaniko/executor --context=$(pwd) --dockerfile=Dockerfile --destination=${DOCKER_IMAGE}:${BUILD_NUMBER}"
      }
    ],
    "inputs": [
      {
        "name": "BUILD_ARTIFACT",
        "type": "string"
      },
      {
        "name": "DOCKER_IMAGE",
        "type": "string",
        "required": true
      }
    ],
    "outputs": [
      {
        "name": "IMAGE_TAG",
        "type": "string",
        "description": "Docker image tag"
      }
    ]
  }'
```

### Stage 5: Deploy to Kubernetes

```bash
curl -X POST https://api.webrobot.eu/api/webrobot/api/pipelines/1/stages \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Deploy to Kubernetes",
    "order": 5,
    "type": "deploy",
    "description": "Deploy application to Kubernetes",
    "when": {
      "condition": "params.DEPLOY_K8S || env.DO_DEPLOY == true"
    },
    "agent": {
      "type": "kubernetes",
      "label": "kubectl",
      "yaml": "apiVersion: v1\nkind: Pod\nspec:\n  containers:\n  - name: kubectl\n    image: alpine/k8s:1.28.2"
    },
    "steps": [
      {
        "type": "script",
        "script": "kubectl apply -f k8s/deployment.yaml -n ${K8S_NAMESPACE}"
      },
      {
        "type": "script",
        "script": "kubectl set image deployment/my-app app=${DOCKER_IMAGE}:${BUILD_NUMBER} -n ${K8S_NAMESPACE}"
      }
    ],
    "inputs": [
      {
        "name": "IMAGE_TAG",
        "type": "string",
        "required": true
      },
      {
        "name": "K8S_NAMESPACE",
        "type": "string",
        "required": true
      }
    ],
    "outputs": [
      {
        "name": "DEPLOYMENT_STATUS",
        "type": "string",
        "description": "Kubernetes deployment status"
      }
    ]
  }'
```

## Step 5: Reorder Stages

If you need to change the order of stages:

```bash
curl -X PUT https://api.webrobot.eu/api/webrobot/api/pipelines/1/stages/3/order \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "order": 2
  }'
```

## Step 6: Generate Jenkinsfile

Once your pipeline is configured, generate the Jenkinsfile YAML:

```bash
curl -X POST https://api.webrobot.eu/api/webrobot/api/pipelines/1/generate \
  -H "X-API-Key: your-api-key" \
  -H "Accept: application/x-yaml"
```

**Response:** Complete Jenkinsfile in YAML format

## Step 7: Update a Stage

Modify an existing stage:

```bash
curl -X PUT https://api.webrobot.eu/api/webrobot/api/pipelines/1/stages/3 \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Build & Test",
    "description": "Build and run tests",
    "steps": [
      {
        "type": "script",
        "script": "npm ci"
      },
      {
        "type": "script",
        "script": "npm test"
      },
      {
        "type": "script",
        "script": "npm run build"
      }
    ]
  }'
```

## Step 8: Delete a Stage

Remove a stage from the pipeline:

```bash
curl -X DELETE https://api.webrobot.eu/api/webrobot/api/pipelines/1/stages/3 \
  -H "X-API-Key: your-api-key"
```

## Python Example

Here's a complete Python example:

```python
import requests

API_BASE = "https://api.webrobot.eu/api"
API_KEY = "your-api-key"
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Create pipeline
pipeline_data = {
    "projectId": "your-project-id",
    "name": "my-pipeline",
    "description": "My first CI/CD pipeline",
    "repositoryUrl": "https://github.com/your-org/your-repo",
    "dockerImage": "ghcr.io/your-org/your-app",
    "k8sNamespace": "webrobot",
    "k8sContext": "webrobot",
    "enabled": True
}

response = requests.post(
    f"{API_BASE}/webrobot/api/pipelines",
    headers=HEADERS,
    json=pipeline_data
)
pipeline = response.json()
pipeline_id = pipeline["id"]

# Add stage
stage_data = {
    "name": "Build",
    "order": 1,
    "type": "build",
    "description": "Build application",
    "agent": {
        "type": "kubernetes",
        "label": "nodejs"
    },
    "steps": [
        {"type": "script", "script": "npm ci"},
        {"type": "script", "script": "npm run build"}
    ],
    "inputs": [],
    "outputs": [
        {
            "name": "BUILD_ARTIFACT",
            "type": "string",
            "description": "Path to build artifact"
        }
    ]
}

response = requests.post(
    f"{API_BASE}/webrobot/api/pipelines/{pipeline_id}/stages",
    headers=HEADERS,
    json=stage_data
)

# Generate Jenkinsfile
response = requests.post(
    f"{API_BASE}/webrobot/api/pipelines/{pipeline_id}/generate",
    headers={**HEADERS, "Accept": "application/x-yaml"}
)
jenkinsfile = response.text
print(jenkinsfile)
```

## Next Steps

- Learn about [available pipeline stages](pipeline-stages.md)
- Explore the [API Reference](../openapi.yaml) for complete endpoint documentation
- Check out advanced features like conditional stages and parallel execution

