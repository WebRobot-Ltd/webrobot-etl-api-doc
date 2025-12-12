# WebRobot ETL API Documentation

Welcome to the WebRobot ETL API documentation. This site provides comprehensive guides and API reference for building and managing ETL pipelines.

## Quick Start

Get started with the WebRobot ETL API in minutes:

1. **Authentication**: Use API Keys for all requests
   ```bash
   curl -H "X-API-Key: your-api-key" https://api.webrobot.eu/api/webrobot/api/projects
   ```

2. **Create a Project**: Set up your first project
   ```bash
   curl -X POST https://api.webrobot.eu/api/webrobot/api/projects \
     -H "X-API-Key: your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"name": "my-project", "description": "My first project"}'
   ```

3. **Build a Pipeline**: Follow our [step-by-step guide](guides/build-a-pipeline.md) to create your first CI/CD pipeline

## Documentation Sections

### 📚 Guides
- **[Build a Pipeline](guides/build-a-pipeline.md)**: Step-by-step tutorial for creating Jenkins pipelines
- **[Pipeline Stages Reference](guides/pipeline-stages.md)**: Complete reference of available pipeline stages

### 📖 API Reference
- **[WebRobot ETL API](openapi.yaml)**: Complete OpenAPI specification with interactive documentation

## Features

- **Pipeline Management**: Create, update, and manage CI/CD pipelines programmatically
- **Stage Configuration**: Define custom stages with input/output specifications
- **Code Generation**: Automatic YAML generation from database configuration
- **Multi-Environment**: Support for dev, staging, and production environments

## Base URLs

- **Production**: `https://api.webrobot.eu/api`
- **Development**: `http://localhost:8020/api`

## Authentication

All API requests require an API key in the `X-API-Key` header:

```
X-API-Key: {organization}:{key}
```

Example:
```
X-API-Key: super-admin-dev:W3bR0b0t-Sup3r-4dm1n-D3v-K3y-2024-S3cur3!
```

## Rate Limiting

Requests are limited to **1000 requests per minute** per API key.

## Support

For questions or issues:
- **Email**: support@webrobot.eu
- **Documentation**: [webrobot.eu](https://webrobot.eu)

---

**Version**: 1.0.0  
**Last Updated**: December 2025

