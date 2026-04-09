# Fitness Analytics Data Engineering Project (v3)

## What is this project?

This is a **production-style data engineering project** that builds a complete pipeline around personal fitness data (cycling, running, walking, etc.) using modern tools.

The project simulates a real-world system where data is:

* Extracted from an API (Strava)
* Stored as raw data
* Processed using distributed computing
* Loaded into a warehouse
* Visualized for insights



---

## Architecture (High-Level)

**Strava API → Airflow → MinIO → Spark → PostgreSQL → Metabase**

* **Orchestration**: Airflow DAGs
* **Raw Storage**: MinIO (S3-compatible)
* **Processing**: Apache Spark on Kubernetes
* **Warehouse**: PostgreSQL
* **Visualization**: Metabase
* **Infra**: Docker + Kubernetes

---

## Project Structure (Important Parts Explained)

### 🔹 Airflow (Orchestration)

```
airflow/
 ├── dags/
 │   ├── dag1_fetchData.py
 │   ├── dag2_sparkProcessing.py
 │   ├── dag3_postgres_object_creation.py
 │   ├── dag4_postgres_object_deletion.py
 │   └── dag5_data_insert_into_postgres.py
 │
 │   ├── ddl/
 │   │   ├── create_objects.sql
 │   │   └── delete_objects.sql
 │
 │   ├── spark/
 │   │   ├── sparkapplicationDataProcessing.yml
 │   │   └── sparkapplicationDataInsertion.yml
 │
 │   └── utils/
 │       ├── commonUtils.py
 │       ├── constants.py
 │       └── defaults.py
```


---

### 🔹 Spark (Processing Layer)

```
spark/
 ├── jobs/
 │   ├── atheleteAndActivitiesProcessing.py
 │   └── data_insert_in_postgres.py
 │
 ├── utils/
 └── config.py
```

Responsible for:

* Cleaning raw JSON data
* Transforming fitness data
* Writing to PostgreSQL

---

### 🔹 Strava Module (API Integration)

```
strava_module/
 ├── auth.py
 ├── client.py
 ├── loader.py
 └── bootstrap_auth.py
```

Handles:

* Authentication
* Token refresh
* API requests

---

### 🔹 Kubernetes (Deployment)

```
k8/
 ├── airflow/
 ├── postgres/
 ├── minio/
 ├── spark/
 ├── metabase/
 └── strava/
```
Contains all manifests for deploying services

---

### 🔹 Docker

```
docker/
 ├── airflow/
 └── spark/
```

Custom images for Airflow and Spark

---

### 🔹 Data (Local Testing)

```
data/
 ├── activities.json
 ├── athlete.json
 └── synthetic_fitness_6_months.csv
```

---

### 🔹 Documentation

```
docs/
├── metabase.md
├── Strava_API_Complete_Setup_Guide.md
├── Strava_API_Registration_Guide.md
└── Strava_Tokens_Explanation.md
```

---

## How to Run the Project

### 1. Clone Repository

```bash
git clone https://github.com/pindio58/fitness-analytics-v3.git
cd fitness-analytics-v3
```

---

### 2. Configure Secrets (VERY IMPORTANT)

You must create actual config/secret files from the provided templates. After copying, make sure to update the values (e.g., credentials, configs) inside these files before deploying.

#### Airflow


```bash
cp k8/airflow/base/airflow-secret.template.yml k8/airflow/base/airflow-secret.yml
cp k8/airflow/base/airflow-configmap.template.yml k8/airflow/base/airflow-configmap.yml

```

#### Strava

```bash
cp k8/strava/base/strava-secret.template.yml k8/strava/base/strava-configmap.template.yml
```

#### PostgreSQL

```bash
cp k8/postgres/base/postgres-secret.template.yml k8/postgres/base/postgres-secret.yml
```

#### MinIO

```bash
cp k8/minio/base/minio-secret.template.yml k8/minio/base/minio-secret.yml
```

#### Spark

```bash
cp k8/spark/base/spark-secret.template.yml k8/spark/base/spark-secret.yml
```

Replace placeholders with real values

---

### 3. Deploy Everything

```bash
chmod +x deploy-all.sh
./deploy-all.sh
```

OR manually:

```bash
kubectl apply -f k8/
```

---

### 4. Verify Deployment

```bash
kubectl get pods
kubectl get svc
```

---

### 5. Access Services (which is already part of `deploy-all.sh`)

#### Airflow

```bash
kubectl port-forward svc/airflow-api-server 8080:8080
```

#### MinIO

```bash
kubectl port-forward svc/fitness-analytics-minio-service 9001:9001
```

#### PostgreSQL

```bash
nohup kubectl port-forward svc/fitness-analytics-postgres-service 5433:5432
```

#### Airflow Postgres
```bash
kubectl port-forward svc/airflow-postgresql  5432:5432
```

#### Metabase

```bash
kubectl port-forward svc/fitness-analytics-metabase-service 3000:3000
```

### 6. Make Airflow connections

#### a. Postgres connection
* Please follow this [link](https://www.notion.so/Integrate-airflow-and-Postgres-2cce0b22664f80428c1bd965e6cad187?v=2cde0b22664f8014b67e000cbb85deb6&source=copy_link)

#### b. Spark connection
* Please follow this [link](https://www.notion.so/Integrate-Airflow-and-Spark-2d0e0b22664f80d5a4a6ef0fc7ce5aa1?v=2cde0b22664f8014b67e000cbb85deb6&source=copy_link)

#### a. MinIo connection
* Please follow step 3 at this [link](https://www.notion.so/Integrate-Airflow-and-MinIO-2cde0b22664f80a49942c5c30262d978?v=2cde0b22664f8014b67e000cbb85deb6&source=copy_link)


### 7. Insert strava token Manually
* Once you have the strava token, please first manually insert the data in table `config.strava_tokens`

---

## Pipeline Flow (DAGs)

### DAG 1 → Fetch Data

* Calls Strava API
* Stores raw JSON in MinIO

### DAG 2 → Spark Processing

* Cleans and transforms data

### DAG 3 → Create Tables

* Executes SQL from `ddl/`

### DAG 4 → Delete Tables (optional)

* Cleanup/reset

### DAG 5 → Insert Data

* Loads processed data into PostgreSQL

---

## Data Architecture (Medallion)

* **Bronze** → Raw JSON (MinIO)
* **Silver** → Cleaned tables
* **Gold** → Aggregated metrics

---

## 📊 Visualization (Metabase)

* Connect to PostgreSQL
* Create dashboards:

  * Distance over time
  * Calories burned
  * Activity types

---

## Important Concepts

### Kubernetes DNS (Very Important)

Inside cluster, always use:

```
<service>.<namespace>.svc.cluster.local
```

Example:

```
fitness-analytics-postgres-service.default.svc.cluster.local
```

Why?

* Pods run in isolated networks
* Short names may fail across namespaces
* Full DNS ensures reliability

---

## Troubleshooting

### Check Logs

```bash
kubectl logs <pod-name>
```

### Describe Pod

```bash
kubectl describe pod <pod-name>
```

### Restart

```bash
kubectl rollout restart deployment <name>
```

---

## Stop Everything

```bash
chmod +x stop-all.sh
./stop-all.sh
```

---

## Future Improvements


* Add Prometheus + Grafana monitoring
* CI/CD pipeline

---

## Why This Project Matters

This project demonstrates:

* Real orchestration (Airflow)
* Distributed processing (Spark)
* Cloud-native infra (Kubernetes)
* Data modeling (warehouse design)



---

## Contributing

Feel free to fork and improve.

---

## 📜 License

MIT
