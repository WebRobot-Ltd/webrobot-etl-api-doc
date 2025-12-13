---
title: Observability & Metrics
version: 1.0.0
description: Comprehensive observability, metrics collection, and pay-to-use billing integration with cloud provider partners
---

# Observability & Metrics

WebRobot provides comprehensive **observability** and **metrics collection** capabilities, with built-in correlation to **pay-to-use billing models** for cloud provider partners.

## Overview

WebRobot's observability stack enables:

- **Real-time monitoring**: Track pipeline execution, resource usage, and performance metrics
- **Cost correlation**: Automatically correlate metrics with cloud provider billing for accurate pay-to-use pricing
- **Multi-cloud support**: Unified metrics collection across different cloud providers (AWS, GCP, Azure, etc.)
- **Partner integration**: Seamless integration with cloud provider billing APIs for transparent cost tracking

## Metrics Collection

### Infrastructure Metrics

WebRobot collects comprehensive infrastructure metrics for each pipeline execution:

#### Resource Usage Metrics

- **CPU Usage**: CPU time consumed (CPU-seconds)
  - Measured per executor and driver
  - Aggregated at job level
  - Unit: CPU-seconds or vCPU-hours

- **Memory Usage**: Peak and average memory consumption
  - Driver memory (GB-hours)
  - Executor memory (GB-hours)
  - Total memory footprint

- **Storage I/O**: Data transfer metrics
  - Input data read (GB)
  - Output data written (GB)
  - S3/MinIO read/write operations
  - Network transfer (GB)

- **Network Metrics**: Network bandwidth and latency
  - Ingress/egress data transfer
  - Cross-region transfer costs
  - API call volumes

#### Execution Metrics

- **Job Duration**: Total execution time
  - Wall-clock time (seconds)
  - Spark application runtime
  - Breakdown by stage

- **Task Metrics**: Spark task-level metrics
  - Tasks completed/failed
  - Shuffle read/write (GB)
  - GC time and frequency

- **Pipeline Stage Metrics**: Per-stage execution metrics
  - Stage duration
  - Records processed
  - Data volume processed

### Business Metrics

- **Records Processed**: Number of records/rows processed
- **Data Volume**: Total data processed (GB)
- **API Calls**: External API calls made during execution
- **Web Requests**: HTTP requests made for web scraping

## Cloud Provider Integration

### Pay-to-Use Billing Model

WebRobot automatically correlates collected metrics with cloud provider billing APIs to enable **transparent pay-to-use pricing**:

#### AWS Integration

- **EC2/EMR Costs**: Correlates CPU-hours, memory-hours with EC2/EMR pricing
- **S3 Costs**: Tracks S3 storage, requests, and data transfer costs
- **Data Transfer**: Monitors cross-region and internet data transfer costs
- **CloudWatch Integration**: Pulls billing data from CloudWatch Billing API

#### GCP Integration

- **Compute Engine Costs**: Correlates vCPU-hours, memory-hours with GCP pricing
- **Cloud Storage Costs**: Tracks GCS storage and operations costs
- **Network Egress**: Monitors network egress costs
- **Billing API Integration**: Uses GCP Billing API for real-time cost tracking

#### Azure Integration

- **VM Costs**: Correlates compute hours with Azure VM pricing
- **Blob Storage Costs**: Tracks Azure Blob storage and operations
- **Data Transfer**: Monitors Azure data transfer costs
- **Cost Management API**: Integrates with Azure Cost Management API

### Cost Attribution

WebRobot provides **granular cost attribution** at multiple levels:

1. **Organization Level**: Total costs per organization
2. **Project Level**: Costs broken down by project
3. **Job Level**: Individual job execution costs
4. **Pipeline Level**: Costs per pipeline definition
5. **Stage Level**: Cost breakdown by pipeline stage

### Billing Transparency

- **Real-time Cost Tracking**: Monitor costs as jobs execute
- **Cost Forecasting**: Estimate costs before job execution
- **Cost Optimization**: Recommendations for cost reduction
- **Multi-currency Support**: Support for different cloud provider currencies

## Observability Stack

### Metrics Storage

WebRobot persists all metrics directly in the **database** for:

- **Reliability**: Direct database persistence ensures metrics are never lost
- **Query Performance**: Fast queries and aggregations using SQL
- **Data Integrity**: ACID guarantees for metric data consistency
- **Cost Attribution**: Direct correlation with billing and usage data
- **Historical Analysis**: Long-term storage and analysis of historical metrics

**Database Schema**:
- Metrics are stored in dedicated tables with proper indexing
- Time-series data optimized for range queries
- Aggregated metrics for fast dashboard queries
- Raw metrics for detailed analysis

### Logging

- **Structured Logging**: JSON-formatted logs for easy parsing
- **Log Levels**: DEBUG, INFO, WARN, ERROR with appropriate filtering
- **Log Correlation**: Trace IDs for correlating logs across services
- **Database Persistence**: Critical logs persisted to database for audit and analysis
- **Retention Policies**: Configurable log retention based on organization tier

### Tracing

- **Distributed Tracing**: OpenTelemetry-compatible tracing
- **Span Correlation**: Correlate traces with metrics and logs
- **Performance Analysis**: Identify bottlenecks and optimization opportunities
- **Database Storage**: Trace data persisted for historical analysis

## Data Access & Post-Processing

### Trino Integration

WebRobot uses **Trino** (formerly PrestoSQL) for post-processing queries on datasets produced by Spark pipelines.

#### Dataset Indexing

All datasets produced by Spark pipelines are **automatically indexed in Trino**:

- **Automatic Registration**: When a pipeline execution completes and writes data to S3/MinIO, the dataset is automatically registered in Trino
- **Schema Discovery**: Trino automatically discovers the schema from the stored data (Parquet, Delta, Iceberg, etc.)
- **Catalog Integration**: Datasets are registered in Trino catalogs (e.g., `s3`, `minio`, `hive`) based on storage location
- **Metadata Management**: Table metadata is maintained in Trino's metastore for fast query planning

#### Post-Processing Queries

The WebRobot API uses **Trino for all post-processing queries**:

- **SQL Interface**: Query datasets using standard SQL through Trino
- **Performance**: Trino's distributed query engine provides fast analytical queries
- **Federation**: Query across multiple data sources (S3, databases, etc.) in a single query
- **API Integration**: All dataset query endpoints use Trino under the hood

#### Benefits

- **Fast Queries**: Trino's columnar processing and distributed execution for fast analytical queries
- **Standard SQL**: Use familiar SQL syntax for data exploration and analysis
- **Unified Access**: Single query interface for all datasets regardless of storage format
- **Real-time Access**: Query data immediately after pipeline execution completes

### Query API

#### Query Dataset

```http
POST /api/webrobot/api/projects/{projectId}/jobs/{jobId}/datasets/{datasetId}/query
```

**Request Body**:
```json
{
  "sql": "SELECT * FROM dataset_table WHERE column = 'value' LIMIT 100",
  "format": "json"
}
```

**Response**:
```json
{
  "queryId": "query-123",
  "status": "completed",
  "rows": [
    { "column1": "value1", "column2": "value2" },
    { "column1": "value3", "column2": "value4" }
  ],
  "rowCount": 2,
  "executionTimeMs": 150
}
```

#### Get Dataset Schema

```http
GET /api/webrobot/api/projects/{projectId}/jobs/{jobId}/datasets/{datasetId}/schema
```

**Response**:
```json
{
  "datasetId": "dataset-123",
  "tableName": "s3.default.pipeline_output",
  "schema": {
    "columns": [
      { "name": "id", "type": "bigint" },
      { "name": "title", "type": "varchar" },
      { "name": "price", "type": "double" },
      { "name": "created_at", "type": "timestamp" }
    ]
  },
  "rowCount": 1000000,
  "sizeBytes": 52428800
}
```

## API Endpoints

### Metrics API

#### Get Job Metrics

```http
GET /api/webrobot/api/projects/{projectId}/jobs/{jobId}/executions/{executionId}/metrics
```

**Response**:
```json
{
  "executionId": "exec-123",
  "jobId": "job-456",
  "metrics": {
    "infrastructure": {
      "cpuSeconds": 3600,
      "memoryGbHours": 8.5,
      "storageReadGb": 100,
      "storageWriteGb": 50,
      "networkTransferGb": 5
    },
    "execution": {
      "durationSeconds": 1800,
      "tasksCompleted": 1000,
      "recordsProcessed": 1000000,
      "dataVolumeGb": 150
    },
    "costs": {
      "computeCost": 12.50,
      "storageCost": 2.30,
      "networkCost": 0.50,
      "totalCost": 15.30,
      "currency": "USD"
    }
  },
  "cloudProvider": "aws",
  "region": "us-east-1"
}
```

#### Get Cost Breakdown

```http
GET /api/webrobot/api/projects/{projectId}/jobs/{jobId}/executions/{executionId}/costs
```

**Response**:
```json
{
  "executionId": "exec-123",
  "costBreakdown": {
    "compute": {
      "driver": {
        "instanceType": "m5.xlarge",
        "hours": 0.5,
        "cost": 5.00
      },
      "executors": {
        "instanceType": "m5.2xlarge",
        "count": 3,
        "hours": 0.5,
        "cost": 7.50
      }
    },
    "storage": {
      "s3Read": {
        "gb": 100,
        "cost": 2.00
      },
      "s3Write": {
        "gb": 50,
        "cost": 0.30
      }
    },
    "network": {
      "dataTransfer": {
        "gb": 5,
        "cost": 0.50
      }
    },
    "total": 15.30,
    "currency": "USD"
  }
}
```

#### Get Organization Metrics Summary

```http
GET /api/webrobot/api/organizations/{orgId}/metrics?startDate=2025-01-01&endDate=2025-01-31
```

**Query Parameters**:
- `startDate`: Start date for metrics aggregation (ISO 8601)
- `endDate`: End date for metrics aggregation (ISO 8601)
- `groupBy`: Group by `project`, `job`, `pipeline` (default: `project`)

**Response**:
```json
{
  "organizationId": "org-123",
  "period": {
    "start": "2025-01-01T00:00:00Z",
    "end": "2025-01-31T23:59:59Z"
  },
  "summary": {
    "totalJobs": 150,
    "totalExecutions": 500,
    "totalCost": 1250.75,
    "totalCpuHours": 720,
    "totalMemoryGbHours": 1200,
    "totalDataProcessedGb": 5000
  },
  "breakdown": [
    {
      "projectId": "proj-1",
      "projectName": "E-commerce Scraping",
      "jobs": 50,
      "executions": 200,
      "cost": 500.25,
      "cpuHours": 300,
      "memoryGbHours": 500
    }
  ]
}
```

### Logs API

#### Get Execution Logs

```http
GET /api/webrobot/api/projects/{projectId}/jobs/{jobId}/executions/{executionId}/logs?podType=driver&tail=100
```

**Query Parameters**:
- `podType`: `driver` (default) or `executor`
- `tail`: Number of lines from the end (default: 100)
- `level`: Filter by log level (`DEBUG`, `INFO`, `WARN`, `ERROR`)

### Dashboards & Visualization

WebRobot provides **API-based dashboards** that query metrics directly from the database:

- **Organization Dashboard**: Overview of all projects and costs (via API endpoints)
- **Project Dashboard**: Detailed project metrics and costs
- **Job Dashboard**: Individual job execution metrics
- **Cost Dashboard**: Cost analysis and trends
- **Real-time Metrics**: Live metrics via WebSocket or polling APIs

**Dashboard API Endpoints**:
- All dashboard data is served via REST API endpoints
- Clients can build custom visualizations using the metrics API
- Real-time updates via WebSocket connections for live dashboards

## Partner Integration

### Cloud Provider Partner Billing

WebRobot integrates with cloud provider partners to enable **transparent pay-to-use billing**:

#### Billing API Integration

- **Real-time Cost Sync**: Automatically sync costs from cloud provider billing APIs
- **Cost Reconciliation**: Reconcile WebRobot metrics with provider billing data
- **Invoice Generation**: Generate detailed invoices based on actual usage
- **Multi-provider Support**: Support for multiple cloud providers in a single organization

#### Usage-Based Pricing

WebRobot enables **usage-based pricing models** for partners:

- **Per-execution pricing**: Charge based on number of job executions
- **Resource-based pricing**: Charge based on CPU-hours, memory-hours, data processed
- **Tiered pricing**: Different rates based on usage tiers
- **Custom pricing models**: Flexible pricing models based on partner agreements

### Partner Dashboard

Cloud provider partners can access:

- **Usage Analytics**: Detailed usage analytics per customer
- **Revenue Tracking**: Track revenue from WebRobot usage
- **Cost Analysis**: Analyze costs and margins
- **Customer Insights**: Understand customer usage patterns

## Best Practices

### Cost Optimization

1. **Right-sizing**: Choose appropriate instance types based on workload
2. **Spot Instances**: Use spot instances for non-critical workloads
3. **Data Locality**: Minimize cross-region data transfer
4. **Caching**: Cache frequently accessed data to reduce I/O costs
5. **Batch Processing**: Batch multiple operations to reduce API call costs

### Monitoring

1. **Set Alerts**: Configure alerts for cost thresholds and anomalies
2. **Regular Reviews**: Review costs regularly to identify optimization opportunities
3. **Cost Attribution**: Use cost attribution to understand spending patterns
4. **Forecasting**: Use cost forecasting to plan budgets

## Security & Privacy

- **Data Isolation**: Metrics and logs are isolated per organization
- **Access Control**: Role-based access control for metrics and cost data
- **Encryption**: All metrics and logs are encrypted at rest and in transit
- **Compliance**: Support for GDPR, SOC 2, and other compliance requirements

---

**Related Guides**:
- [Build a Pipeline](build-a-pipeline.md)
- [Pipeline Stages Reference](pipeline-stages.md)
- [Technical Partners](technical-partners.md)

