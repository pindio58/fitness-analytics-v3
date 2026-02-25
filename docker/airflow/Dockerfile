ARG AIRFLOW_IMAGE=apache/airflow:3.0.2
FROM ${AIRFLOW_IMAGE}

USER root

# did not use dags in target because gitsync overrides everything
COPY airflow/dags/ddl /opt/airflow/ddl
COPY airflow/dags/spark /opt/airflow/spark
COPY airflow/dags/utils /opt/airflow/utils
COPY data /opt/airflow/data
COPY airflow/settings.py /opt/airflow/settings.py

RUN chown -R airflow: /opt/airflow

USER  airflow

ENV PYTHONPATH="/opt/airflow"