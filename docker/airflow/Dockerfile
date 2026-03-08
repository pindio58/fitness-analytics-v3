ARG AIRFLOW_IMAGE=apache/airflow:3.0.2
FROM ${AIRFLOW_IMAGE}

USER root

# did not use dags in target because gitsync overrides everything
COPY airflow/dags/ddl /opt/airflow/ddl
COPY airflow/dags/spark /opt/airflow/spark
COPY airflow/dags/utils /opt/airflow/utils
COPY data /opt/airflow/data
COPY airflow/constants.py /opt/airflow/constants.py
COPY strava_module /opt/airflow/strava_module


RUN chown -R airflow: /opt/airflow

USER  airflow
RUN pip install --no-cache-dir \
        requests \
        python-dotenv \
        pydantic \
        pydantic-settings

ENV PYTHONPATH="/opt/airflow"