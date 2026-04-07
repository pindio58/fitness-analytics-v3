# Metabase → PostgreSQL Connection (Kubernetes)

## Connection Settings

Use the following configuration in Metabase:

```
Database Type: PostgreSQL
Host: fitness-analytics-postgres-statefulset-0.fitness-analytics-postgres-service
Port: 5432
Database: <your_db>
Username: <your_user>
Password: <your_password>
SSL: OFF
```

---

## Why Full DNS is Required

### Service Configuration

Your PostgreSQL service is defined as:

```
clusterIP: None
```

This makes it a **headless service**.

---

### Behavior of Headless Service

A headless service does NOT provide a single stable IP.

Instead, DNS returns:

```
Multiple Pod IPs
```

Example:

```
fitness-analytics-postgres-service → [IP1, IP2, IP3]
```

---

### Issue with Metabase

Metabase (JDBC client):

* Selects one IP from DNS
* Does not retry across multiple IPs reliably
* Connection may fail

---

### Why Full DNS Works

Using:

```
fitness-analytics-postgres-statefulset-0.fitness-analytics-postgres-service
```

Resolves to:

```
Exactly one PostgreSQL pod
```

Result:

* Stable connection
* No ambiguity
* Works reliably with Metabase

---

## Summary

* Headless service → multiple IPs → not reliable for some clients
* Full pod DNS → single endpoint → reliable connection
