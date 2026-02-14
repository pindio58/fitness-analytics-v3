--Create Schema --
CREATE SCHEMA IF NOT EXISTS fitness;


--Create table

CREATE TABLE IF NOT EXISTS fitness.fact_daily_workouts (
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


-- Indexes

-- B-tree index on date
CREATE INDEX IF NOT EXISTS idx_fact_daily_workouts_date ON fitness.fact_daily_workouts (date);

-- B-tree index on workout_type
CREATE INDEX IF NOT EXISTS idx_fact_daily_workouts_workout_type ON fitness.fact_daily_workouts (workout_type);

-- Partial index for faster filtering when did_run = true
CREATE INDEX IF NOT EXISTS idx_fact_daily_workouts_did_run_true ON fitness.fact_daily_workouts (did_run)
WHERE did_run = true;
