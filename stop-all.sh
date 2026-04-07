#!/usr/bin/env bash
set -e

# Centralized stop script for fitness-analytics-v3
# Usage: ./stop-all.sh

WORKDIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K8_DIR="$WORKDIR/k8"
LOG_FILE="$WORKDIR/stop-all.log"

# Redirect all output to log file and console
exec > >(tee -a "$LOG_FILE") 2>&1

echo "Stopping port-forwarding..."
# Kill all kubectl port-forward processes
pkill -f "kubectl port-forward" || true


echo "Uninstalling Airflow and Spark Helm releases..."
helm uninstall airflow -n fitness-analytics-namespace || true
helm uninstall spark-operator -n fitness-analytics-namespace || true

echo "Deleting all resources for MinIO, Postgres, Airflow, Spark..."
kubectl delete -f "$K8_DIR/minio/base" || true
kubectl delete -f "$K8_DIR/postgres/base" || true
kubectl delete -f "$K8_DIR/airflow/base" || true
kubectl delete -f "$K8_DIR/spark/base" || true
kubectl delete -f "$K8_DIR/metabase/base" || true

echo "All services stopped and resources deleted."
