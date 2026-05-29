# Cluster to Cluster Migration (AZURE)

Zero downtime migration pipeline from AWS to Azure using Kafka, Druid, MongoDB, Redis, and Kubernetes.

## Architecture

Source (AKS - source namespace)          Destination (AKS - destination namespace)
─────────────────────────────            ────────────────────────────────────────
PostgreSQL (device/asset data)    ──►    MongoDB (migrated records)
Kafka + ZooKeeper (streaming)     ──►    Apache Druid (real-time analytics)
Redis (caching)                          Redis (caching)
Data Generator (dummy telemetry)         Kafka Consumer
Debezium (CDC)

## Tech Stack

- **Kubernetes** — Azure AKS (East US)
- **Apache Kafka** — event streaming backbone
- **Apache Druid** — real-time telemetry analytics
- **MongoDB** — destination document store
- **PostgreSQL** — source relational database
- **Redis** — caching layer
- **Debezium** — Change Data Capture (CDC) for zero downtime
- **Terraform** — Infrastructure as Code
- **GitHub Actions** — CI/CD pipeline

## Data Streams

| Topic | Description | Destination |
|-------|-------------|-------------|
| telemetry | Voltage, current, temperature, power from 5 devices every 2s | Druid + MongoDB |
| events | Threshold breaches, alerts, device incidents | Druid + MongoDB |
| logs | INFO/WARN/ERROR logs from all devices | MongoDB |
| CDC streams | PostgreSQL change capture via Debezium | MongoDB |

## Dummy Data

Simulates SH industrial IoT:
- 5 devices across Mumbai, Pune, Delhi plants
- Circuit breakers, power meters, UPS, transformers, solar inverters
- Continuous telemetry at 2 second intervals

## Project Structure

aws-aks-migration/
├── terraform/
│   ├── aws/          # EKS infrastructure (reference)
│   └── azure/        # AKS cluster provisioning
├── kafka/            # Kafka, ZooKeeper, PostgreSQL, Redis manifests
├── druid/            # Druid cluster manifests + Kafka supervisors
├── mongo/            # MongoDB manifests
├── developer_code_1/ # Data generator + Kafka consumer
└── .github/
└── workflows/    # Terraform + Deploy CI/CD pipelines

## CI/CD

- Push to `terraform/` triggers Terraform workflow and provisions AKS
- Push to `developer_code_1/` triggers Deploy workflow, builds Docker images, pushes to ACR, deploys to AKS

## Zero Downtime Migration Strategy

1. Source PostgreSQL keeps running
2. Debezium captures every change (INSERT/UPDATE/DELETE)
3. Changes stream to Kafka topics
4. Consumer writes to MongoDB in real time
5. When lag = 0, cutover happens — no downtime

## Quick Start

```bash
# Connect to AKS
az aks get-credentials --resource-group sh-migration-rg --name sh-aks

# Check source namespace
kubectl get pods -n source

# Check destination namespace
kubectl get pods -n destination

# Access Druid console
kubectl port-forward -n destination svc/druid-router 8888:8888
# Open http://localhost:8888
```