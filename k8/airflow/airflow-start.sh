#!/usr/bin/env bash
helm upgrade --install airflow apache-airflow/airflow -f ./values-dev.yml