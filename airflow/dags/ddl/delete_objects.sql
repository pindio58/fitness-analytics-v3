-- DROP EVERYTHING --

DROP SCHEMA IF EXISTS {{ params.gold_schema }} CASCADE;
DROP SCHEMA IF EXISTS {{ params.silver_schema }} CASCADE;
DROP SCHEMA IF EXISTS {{ params.bronze_schema }} CASCADE;
DROP SCHEMA IF EXISTS {{ params.config_schema }} CASCADE;