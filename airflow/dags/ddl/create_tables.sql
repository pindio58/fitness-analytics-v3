--Create Schema --
CREATE SCHEMA IF NOT EXISTS {{ params.schema }};


--Create table fitness

CREATE TABLE IF NOT EXISTS {{ params.schema }}.{{ params.fitness_table }} (
    date DATE NOT NULL,
    day_of_week VARCHAR(9),
    workout_type VARCHAR(50),

    run_distance_km DOUBLE PRECISION,
    run_duration_min DOUBLE PRECISION,
    avg_pace_min_per_km DOUBLE PRECISION,

    boxing_duration_min DOUBLE PRECISION,
    skipping_duration_min DOUBLE PRECISION,
    desi_workout_duration_min DOUBLE PRECISION,
    total_duration_min DOUBLE PRECISION,

    avg_heart_rate_bpm INTEGER,
    max_heart_rate_bpm INTEGER,
    calories_burned INTEGER,
    steps INTEGER,

    did_run BOOLEAN,
    did_box BOOLEAN,
    did_skip BOOLEAN,
    did_desi_workout BOOLEAN,

    calories_per_min DOUBLE PRECISION,
    calories_per_km DOUBLE PRECISION,
    workout_density DOUBLE PRECISION,

    year INTEGER,
    month INTEGER,
    week_of_year INTEGER,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),

    PRIMARY KEY (date)
);

-- https://www.notion.so/make-another-table-for-token-storage-31ae0b22664f8022aa2add1e6fb773bf?v=2cde0b22664f8014b67e000cbb85deb6&source=copy_link
-- create table for token store


CREATE TABLE {{ params.schema }}.{{ params.token_table }}  (
    athlete_id BIGINT PRIMARY KEY,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes

-- B-tree index on date
CREATE INDEX IF NOT EXISTS idx_fact_daily_workouts_date ON fitness.fact_daily_workouts (date);

-- B-tree index on workout_type
CREATE INDEX IF NOT EXISTS idx_fact_daily_workouts_workout_type ON fitness.fact_daily_workouts (workout_type);

-- Partial index for faster filtering when did_run = true
CREATE INDEX IF NOT EXISTS idx_fact_daily_workouts_did_run_true ON fitness.fact_daily_workouts (did_run)
WHERE did_run = true;
