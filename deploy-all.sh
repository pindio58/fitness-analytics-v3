
#!/usr/bin/env bash
set -e

# Centralized deployment script for fitness-analytics-v3
# Usage: ./deploy-all.sh

WORKDIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K8_DIR="$WORKDIR/k8"
LOG_FILE="$WORKDIR/deploy-all.log"

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

## 2. Postgres: apply base YAMLs
apply_folder "$K8_DIR/postgres/base"

## 3. Airflow: apply base YAMLs, then start
apply_folder "$K8_DIR/airflow/base"

## 4. Metabase: apply base YAMLs, then start
apply_folder "$K8_DIR/metabase/base"

cd "$K8_DIR/airflow"
./airflow-start.sh
cd "$WORKDIR"

## 5. Spark: apply base YAMLs, then start
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
# Metabase webserver (default 3000)
nohup kubectl port-forward svc/fitness-analytics-metabase-service 3000:3000 -n fitness-analytics-namespace > "$WORKDIR/metabase-port.log" 2>&1 &
# Spark UI (default 4040)
# nohup kubectl port-forward svc/spark 4040:4040 -n fitness-analytics-namespace > "$WORKDIR/spark-port.log" 2>&1 &

echo "Deployment and port-forwarding started."
