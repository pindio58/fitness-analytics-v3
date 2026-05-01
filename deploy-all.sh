
#!/usr/bin/env bash
set -e

# Centralized deployment script for fitness-analytics-v3
# Usage: ./deploy-all.sh

WORKDIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K8_DIR="$WORKDIR/k8"
LOG_FILE="$WORKDIR/logsOfDeploy.log"

# Redirect all output to log file and console
exec > >(tee -a "$LOG_FILE") 2>&1

# Helper function for kubectl apply
apply_folder() {
  local folder="$1"
  echo "Applying all YAMLs in $folder"
  kubectl apply -f "$folder"
}

## 1. MinIO: apply base YAMLs
apply_folder "$K8_DIR/minio/base"

## 2. Strava: apply base YAMLs
apply_folder "$K8_DIR/strava/base"

## 3. Postgres: apply base YAMLs
apply_folder "$K8_DIR/postgres/base"

## 4. Prometheus: apply base YAMLs, then start prmetheus, statsd and postgresdb exporter
apply_folder "$K8_DIR/prometheus/base"
cd "$K8_DIR/prometheus"
./prom-start.sh
./statsd-start.sh
./postgresexporter-start.sh
cd "$WORKDIR"

## 5. Metabase: apply base YAMLs, then start
apply_folder "$K8_DIR/metabase/base"

## 6. Airflow: apply base YAMLs, then start
apply_folder "$K8_DIR/airflow/base"

cd "$K8_DIR/airflow"
./airflow-start.sh
cd "$WORKDIR"

## 7. Spark: apply base YAMLs, then start
apply_folder "$K8_DIR/spark/base"
cd "$K8_DIR/spark"
./spark-start.sh
cd "$WORKDIR"

# 6. Port-forwarding for all services

echo "Starting port-forwarding..."
# MinIO (default 9001)
nohup kubectl port-forward svc/fitness-analytics-minio-service 9001:9001 -n fitness-analytics-namespace > "$WORKDIR/minio-port.log" 2>&1 &
# Postgres (default 5432)
nohup kubectl port-forward svc/fitness-analytics-postgres-service 5433:5432 -n fitness-analytics-namespace > "$WORKDIR/postgres-port.log" 2>&1 &
# Airflow webserver (default 8080)
nohup kubectl port-forward svc/airflow-api-server 8080:8080 -n fitness-analytics-namespace > "$WORKDIR/airflow-port.log" 2>&1 &
# Airflow postgres 
nohup kubectl port-forward svc/airflow-postgresql  5432:5432 -n fitness-analytics-namespace > "$WORKDIR/airflow-port.log" 2>&1 &
# Metabase webserver (default 3000)
nohup kubectl port-forward svc/fitness-analytics-metabase-service 3000:3000 -n fitness-analytics-namespace > "$WORKDIR/metabase-port.log" 2>&1 &
# Spark UI (default 4040)
# nohup kubectl port-forward svc/spark 4040:4040 -n fitness-analytics-namespace > "$WORKDIR/spark-port.log" 2>&1 &

# Prometheus webserver (default 9090)
nohup kubectl port-forward svc/prometheus-kube-prometheus-prometheus  9090:9090 -n fitness-analytics-namespace > "$WORKDIR/metabase-port.log" 2>&1 &

echo "Deployment and port-forwarding started."
