#!/usr/bin/env bash
helm install spark-operator spark-operator/spark-operator -n fitness-analytics-namespace -f spark-values.yml --set "spark.jobNamespaces={fitness-analytics-namespace}"