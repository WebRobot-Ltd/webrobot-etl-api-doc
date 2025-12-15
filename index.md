---
title: WebRobot ETL API Documentation
version: 1.0.0
description: Comprehensive guides and API reference for building and managing ETL pipelines
---

# WebRobot ETL API Documentation

## Language / Lingua / Γλώσσα

- **English**: continue on this page (default) or go to `guides/`
- **Italiano**: vai a **[`it/index.md`](it/index.md)**
- **Ελληνικά**: πηγαίνετε στο **[`el/index.md`](el/index.md)**

---

## About WebRobot

**WebRobot** is a **Spark-native, API-first data infrastructure** for building **agentic ETL pipelines** and **data products**.

This documentation covers the **ETL component** of WebRobot, which provides:

- **Spark-native processing**: Built on Apache Spark for scalable data processing
- **API-first architecture**: Manage pipelines, projects, and jobs via REST API
- **Agentic capabilities**: LLM-powered intelligent stages for adaptive web scraping and data extraction
- **Maximum extensibility**: The agentic nature requires maximum pipeline extensibility, enabled through **Python Extensions** for auto-programming custom stages without compiling plugins
- **Extensible framework**: Custom plugins (for technical partners), stages, resolvers, and Python extensions (for admin and technical partners)

## AI Agent Integration & MCP Protocol

This documentation serves as a **reference knowledge base** for AI agents and development tools:

### 🤖 AI Agent Support

This documentation is designed to be consumed by AI coding assistants and agents, including:

- **Cursor AI**: Integrated AI assistant for code generation and pipeline creation
- **ChatGPT**: Reference documentation for WebRobot ETL capabilities
- **Claude Desktop**: Knowledge base for understanding WebRobot architecture and APIs
- **Integrated Development Agent**: Built-in AI agent within WebRobot for automated pipeline generation and optimization

### 🔌 Model Context Protocol (MCP)

All WebRobot ETL functionalities are exposed via **MCP (Model Context Protocol) endpoints**, enabling:

- **Standardized AI integration**: Consistent interface for AI agents to interact with WebRobot
- **Function calling**: AI agents can invoke WebRobot operations through MCP tools
- **Context-aware assistance**: Agents can query pipeline schemas, stage capabilities, and API specifications
- **Automated pipeline generation**: AI agents can create, validate, and execute pipelines programmatically

Every feature documented here is accessible both via REST API and MCP endpoints, ensuring seamless integration with AI-powered development workflows.

## Quick Start (EN)

Welcome to the WebRobot ETL API documentation. This site provides comprehensive guides and API reference for building and managing ETL pipelines as part of the WebRobot platform.

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

3. **Build a Pipeline**: Follow our [step-by-step guide](guides/build-a-pipeline.md) to create your first ETL pipeline using YAML syntax

## Documentation Sections

### 📚 Guides
- **[Build a Pipeline](guides/build-a-pipeline.md)**: Guide to building ETL pipelines using YAML syntax, attribute resolvers, custom actions, and Python extensions
- **[Pipeline Stages Reference](guides/pipeline-stages.md)**: Complete reference of pipeline stages, YAML syntax, attribute resolvers, custom actions, and Python extensions
- **[Pipeline Examples](guides/pipeline-examples.md)**: Copy-pasteable YAML examples aligned with the current parser and stages
- **[Observability & Metrics](guides/observability-metrics.md)**: Comprehensive observability, metrics collection, and pay-to-use billing integration with cloud provider partners
- **[EAN Image Sourcing Plugin](guides/ean-image-sourcing.md)**: EAN plugin pipeline + CloudCredential injection behavior
- **[Technical Partners](guides/technical-partners.md)**: How to extend WebRobot (API plugins + ETL runtime plugins + Python extensions)

### 🏭 Vertical Use Cases
- **[Vertical Use Cases Overview](guides/vertical-use-cases.md)**: Industry-specific use cases and complete pipeline examples
- **[Price Comparison & E-commerce](guides/vertical-price-comparison.md)**: Aggregate product offers from multiple sources, compare prices, track availability

### 📖 API Reference
- **[WebRobot ETL API](openapi.yaml)**: Complete OpenAPI specification with interactive documentation

## Features

- **Pipeline Management**: Create, update, and manage ETL pipelines programmatically via API
- **YAML Syntax**: Define pipelines using declarative YAML configuration
- **Attribute Resolvers**: Custom extraction methods for flexible data extraction
- **Custom Actions**: Extend browser interactions with custom action factories
- **Python Extensions**: Create custom Python row transform stages (`python_row_transform:<name>`)
- **Intelligent Stages**: LLM-powered stages for adaptive web scraping
- **Observability & Metrics**: Comprehensive metrics collection with real-time monitoring and cost correlation
- **Pay-to-Use Billing**: Automatic correlation of metrics with cloud provider billing for transparent usage-based pricing

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
X-API-Key: your-organization:your-api-key
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

