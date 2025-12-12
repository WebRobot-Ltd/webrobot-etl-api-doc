# Pipeline Stages Reference

Complete reference of available pipeline stages, their configuration options, input/output formats, and usage examples.

## Stage Types

### Native Stages

These are built-in stages provided by Jenkins and the WebRobot platform.

#### 1. Initialize

**Type**: `initialize`  
**Purpose**: Set up build environment and initial variables

**Configuration:**
```json
{
  "name": "Initialize",
  "type": "initialize",
  "order": 1,
  "agent": {
    "type": "any"
  },
  "steps": [
    {
      "type": "script",
      "script": "env.DO_DEPLOY = false"
    }
  ]
}
```

**Inputs**: None  
**Outputs**: 
- `DO_DEPLOY` (boolean): Flag to enable automatic deployment

---

#### 2. Checkout

**Type**: `checkout`  
**Purpose**: Checkout source code from version control

**Configuration:**
```json
{
  "name": "Checkout",
  "type": "checkout",
  "order": 2,
  "agent": {
    "type": "any"
  },
  "steps": [
    {
      "type": "checkout",
      "scm": "git"
    }
  ]
}
```

**Inputs**: None  
**Outputs**:
- `WORKSPACE` (string): Workspace directory path

**Supported SCM**: Git, SVN, Mercurial

---

#### 3. Build

**Type**: `build`  
**Purpose**: Compile and build application

**Configuration:**
```json
{
  "name": "Build",
  "type": "build",
  "order": 3,
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
  ]
}
```

**Inputs**:
- `WORKSPACE` (string, required): Source code directory

**Outputs**:
- `BUILD_ARTIFACT` (string): Path to build artifact
- `BUILD_STATUS` (string): Build status (success/failure)

**Common Build Tools**:
- Node.js: `npm`, `yarn`, `pnpm`
- Java: `maven`, `gradle`
- Python: `pip`, `poetry`
- Go: `go build`

---

#### 4. Test

**Type**: `test`  
**Purpose**: Run unit and integration tests

**Configuration:**
```json
{
  "name": "Test",
  "type": "test",
  "order": 4,
  "agent": {
    "type": "kubernetes",
    "label": "nodejs"
  },
  "steps": [
    {
      "type": "script",
      "script": "npm test"
    },
    {
      "type": "script",
      "script": "npm run test:coverage"
    }
  ]
}
```

**Inputs**:
- `BUILD_ARTIFACT` (string): Build output to test

**Outputs**:
- `TEST_RESULTS` (string): Path to test results XML/JSON
- `COVERAGE_REPORT` (string): Path to coverage report

---

#### 5. Docker Build

**Type**: `docker`  
**Purpose**: Build Docker container image

**Configuration:**
```json
{
  "name": "Build Docker Image",
  "type": "docker",
  "order": 5,
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
  ]
}
```

**Inputs**:
- `BUILD_ARTIFACT` (string): Application to containerize
- `DOCKERFILE` (string): Path to Dockerfile (default: `./Dockerfile`)

**Outputs**:
- `IMAGE_TAG` (string): Docker image tag
- `IMAGE_DIGEST` (string): Image digest

**Builders**:
- Kaniko (Kubernetes-native, no Docker daemon)
- Docker (requires Docker daemon)
- Buildah (alternative container builder)

---

#### 6. Deploy

**Type**: `deploy`  
**Purpose**: Deploy application to target environment

**Configuration:**
```json
{
  "name": "Deploy to Kubernetes",
  "type": "deploy",
  "order": 6,
  "agent": {
    "type": "kubernetes",
    "label": "kubectl",
    "yaml": "apiVersion: v1\nkind: Pod\nspec:\n  containers:\n  - name: kubectl\n    image: alpine/k8s:1.28.2"
  },
  "steps": [
    {
      "type": "script",
      "script": "kubectl apply -f k8s/deployment.yaml -n ${K8S_NAMESPACE}"
    }
  ]
}
```

**Inputs**:
- `IMAGE_TAG` (string, required): Docker image to deploy
- `K8S_NAMESPACE` (string, required): Target Kubernetes namespace
- `MANIFEST_PATH` (string): Path to Kubernetes manifests

**Outputs**:
- `DEPLOYMENT_STATUS` (string): Deployment status
- `SERVICE_URL` (string): Deployed service URL

**Deployment Targets**:
- Kubernetes
- Docker Swarm
- Cloud platforms (AWS ECS, GCP Cloud Run, Azure Container Instances)

---

### Custom Stages

You can define custom stages with specific input/output formats.

#### Custom Stage Example

```json
{
  "name": "Custom Processing",
  "type": "custom",
  "order": 7,
  "description": "Custom data processing stage",
  "agent": {
    "type": "kubernetes",
    "label": "custom",
    "yaml": "apiVersion: v1\nkind: Pod\nspec:\n  containers:\n  - name: processor\n    image: custom-processor:latest"
  },
  "steps": [
    {
      "type": "script",
      "script": "process-data.sh"
    }
  ],
  "inputs": [
    {
      "name": "INPUT_DATA",
      "type": "string",
      "format": "json",
      "required": true,
      "description": "Input data in JSON format"
    },
    {
      "name": "CONFIG_FILE",
      "type": "string",
      "format": "yaml",
      "required": false,
      "description": "Configuration file path"
    }
  ],
  "outputs": [
    {
      "name": "PROCESSED_DATA",
      "type": "string",
      "format": "json",
      "description": "Processed output data"
    },
    {
      "name": "METADATA",
      "type": "object",
      "format": "json",
      "description": "Processing metadata"
    }
  ]
}
```

## Input/Output Formats

### Supported Formats

- **String**: Plain text or file path
- **JSON**: JSON object or array
- **YAML**: YAML configuration
- **Boolean**: True/false flag
- **Number**: Integer or decimal
- **Object**: Complex nested structure

### Format Examples

**JSON Input:**
```json
{
  "name": "CONFIG",
  "type": "object",
  "format": "json",
  "schema": {
    "type": "object",
    "properties": {
      "timeout": {"type": "number"},
      "retries": {"type": "integer"}
    }
  }
}
```

**YAML Input:**
```json
{
  "name": "K8S_MANIFEST",
  "type": "string",
  "format": "yaml",
  "description": "Kubernetes manifest in YAML format"
}
```

## Conditional Execution

Stages can be conditionally executed using `when` clauses:

```json
{
  "name": "Deploy",
  "when": {
    "condition": "params.DEPLOY_K8S == true && env.BUILD_TYPE == 'production'"
  }
}
```

**Supported Conditions**:
- Parameter checks: `params.PARAM_NAME == 'value'`
- Environment variables: `env.VAR_NAME == 'value'`
- Build status: `previousStage.status == 'success'`
- Logical operators: `&&`, `||`, `!`

## Parallel Execution

Run multiple stages in parallel:

```json
{
  "name": "Parallel Tests",
  "type": "parallel",
  "stages": [
    {
      "name": "Unit Tests",
      "order": 1
    },
    {
      "name": "Integration Tests",
      "order": 2
    }
  ]
}
```

## Stage Ordering

Stages are executed in order based on the `order` field. You can reorder stages using the API:

```bash
# Move stage to position 2
curl -X PUT /api/pipelines/{id}/stages/{stageId}/order \
  -d '{"order": 2}'
```

## Best Practices

1. **Input Validation**: Always specify required inputs and their formats
2. **Output Documentation**: Document all outputs for downstream stages
3. **Error Handling**: Define failure conditions and rollback strategies
4. **Resource Limits**: Set appropriate CPU/memory limits for Kubernetes agents
5. **Idempotency**: Ensure stages can be safely re-run

## Stage Templates

Common stage templates are available:

- `nodejs-build`: Node.js application build
- `maven-build`: Java Maven build
- `docker-build`: Docker image build
- `k8s-deploy`: Kubernetes deployment
- `test-runner`: Generic test execution

Use templates to quickly scaffold common pipeline patterns.

