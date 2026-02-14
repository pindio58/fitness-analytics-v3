#!/usr/bin/env bash
kubectl apply -f .
helm upgrade --install airflow apache-airflow/airflow -f ./values-dev.yml