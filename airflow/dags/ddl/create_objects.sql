--Create Schemas --
CREATE SCHEMA IF NOT EXISTS {{ params.bronze_schema }};
CREATE SCHEMA IF NOT EXISTS {{ params.silver_schema }};
CREATE SCHEMA IF NOT EXISTS {{ params.gold_schema }};
CREATE SCHEMA IF NOT EXISTS {{ params.config_schema }};


CREATE TABLE IF NOT EXISTS {{ params.config_schema }}.{{ params.token_table }} 
( 
    athlete_id int8 NOT NULL, 
    access_token text NOT NULL, 
    refresh_token text NOT NULL, 
    expires_at int8 NOT NULL, 
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NULL, 
    CONSTRAINT strava_tokens_pkey PRIMARY KEY (athlete_id)
);


-- Create table athlete under bronze --
CREATE TABLE IF NOT EXISTS {{ params.bronze_schema }}.{{ params.athlete }}
(
    id BIGINT PRIMARY KEY,
    badge_type_id BIGINT,
    bio TEXT,
    city TEXT,
    country TEXT,
    created_at TIMESTAMP,
    firstname TEXT,
    follower TEXT,
    friend TEXT,
    lastname TEXT,
    premium BOOLEAN,
    profile TEXT,
    profile_medium TEXT,
    resource_state BIGINT,
    sex TEXT,
    state TEXT,
    summit BOOLEAN,
    updated_at TIMESTAMP,
    username TEXT,
    weight TEXT
);

-- Create table activities under bronze --
CREATE TABLE IF NOT EXISTS {{ params.bronze_schema }}.{{ params.activities }} (
    id BIGINT PRIMARY KEY,

    achievement_count BIGINT,
    athlete_id BIGINT,
    athlete_resource_state BIGINT,

    athlete_count BIGINT,
    average_cadence DOUBLE PRECISION,
    average_heartrate DOUBLE PRECISION,
    average_speed DOUBLE PRECISION,
    comment_count BIGINT,
    commute BOOLEAN,
    device_name TEXT,
    display_hide_heartrate_option BOOLEAN,
    distance DOUBLE PRECISION,
    elapsed_time BIGINT,
    elev_high DOUBLE PRECISION,
    elev_low DOUBLE PRECISION,

    end_lat DOUBLE PRECISION,
    end_lng DOUBLE PRECISION,

    external_id TEXT,
    flagged BOOLEAN,
    from_accepted_tag BOOLEAN,
    gear_id TEXT,
    has_heartrate BOOLEAN,
    has_kudoed BOOLEAN,
    heartrate_opt_out BOOLEAN,

    kudos_count BIGINT,
    location_city TEXT,
    location_country TEXT,
    location_state TEXT,
    manual BOOLEAN,

    map_id TEXT,
    map_resource_state BIGINT,
    summary_polyline TEXT,

    max_heartrate DOUBLE PRECISION,
    max_speed DOUBLE PRECISION,
    moving_time BIGINT,
    name TEXT,
    photo_count BIGINT,
    pr_count BIGINT,
    private BOOLEAN,
    resource_state BIGINT,
    sport_type TEXT,

    start_date TIMESTAMP,
    start_date_local TIMESTAMP,

    start_lat DOUBLE PRECISION,
    start_lng DOUBLE PRECISION,

    timezone TEXT,
    total_elevation_gain DOUBLE PRECISION,
    total_photo_count BIGINT,
    trainer BOOLEAN,
    type TEXT,
    upload_id BIGINT,
    upload_id_str TEXT,
    utc_offset DOUBLE PRECISION,
    visibility TEXT,
    workout_type BIGINT
);


-- Create table gears under bronze --
CREATE TABLE IF NOT EXISTS {{ params.bronze_schema }}.{{ params.gears }}
(
    id TEXT PRIMARY KEY,

    -- common fields
    is_primary BOOLEAN,
    name TEXT,
    nickname TEXT,
    resource_state BIGINT,
    retired BOOLEAN,
    distance DOUBLE PRECISION,
    converted_distance DOUBLE PRECISION,
    brand_name TEXT,
    model_name TEXT,
    description TEXT,

    -- bike-specific
    weight DOUBLE PRECISION,
    frame_type BIGINT,

    -- shoes-specific
    notification_distance BIGINT,

    -- derived (very useful)
    gear_type TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);


-- Create table activities_enriched under SILVER --
CREATE TABLE IF NOT EXISTS {{ params.silver_schema }}.{{ params.activities_enriched }}
(
    id BIGINT PRIMARY KEY,
    activity_id BIGINT,

    athlete_id BIGINT,
    gear_id TEXT,

    achievement_count BIGINT,
    athlete_count BIGINT,
    average_cadence DOUBLE PRECISION,
    average_heartrate DOUBLE PRECISION,
    average_speed DOUBLE PRECISION,
    comment_count BIGINT,
    commute BOOLEAN,
    device_name TEXT,
    display_hide_heartrate_option BOOLEAN,
    distance DOUBLE PRECISION,
    elapsed_time BIGINT,
    elev_high DOUBLE PRECISION,
    elev_low DOUBLE PRECISION,
    external_id TEXT,
    flagged BOOLEAN,
    from_accepted_tag BOOLEAN,
    has_heartrate BOOLEAN,
    has_kudoed BOOLEAN,
    heartrate_opt_out BOOLEAN,
    kudos_count BIGINT,
    location_city TEXT,
    location_country TEXT,
    location_state TEXT,
    manual BOOLEAN,
    max_heartrate DOUBLE PRECISION,
    max_speed DOUBLE PRECISION,
    moving_time BIGINT,
    name TEXT,
    photo_count BIGINT,
    pr_count BIGINT,
    private BOOLEAN,
    sport_type TEXT,

    start_date TIMESTAMP,
    start_date_local TIMESTAMP,
    timezone TEXT,

    total_elevation_gain DOUBLE PRECISION,
    total_photo_count BIGINT,
    trainer BOOLEAN,
    type TEXT,
    upload_id BIGINT,
    upload_id_str TEXT,
    utc_offset DOUBLE PRECISION,
    visibility TEXT,
    workout_type BIGINT,

    summary_polyline TEXT,
    start_lat DOUBLE PRECISION,
    start_lng DOUBLE PRECISION,
    end_lat DOUBLE PRECISION,
    end_lng DOUBLE PRECISION,

    has_gps BOOLEAN NOT NULL,

    distance_km DOUBLE PRECISION,
    moving_time_min DOUBLE PRECISION,
    elapsed_time_min DOUBLE PRECISION,
    avg_speed_kmh DOUBLE PRECISION,
    max_speed_kmh DOUBLE PRECISION,
    elevation_gain_km DOUBLE PRECISION,

    year INT,
    month INT,
    week INT,
    day DATE,

    pace_min_per_km DOUBLE PRECISION,
    is_long_activity BOOLEAN,
    is_fast_activity BOOLEAN,
    elevation_per_km DOUBLE PRECISION,

    -- athlete denormalized fields
    badge_type_id BIGINT,
    bio TEXT,
    city TEXT,
    country TEXT,
    created_at TIMESTAMP,
    firstname TEXT,
    follower TEXT,
    friend TEXT,
    lastname TEXT,
    premium BOOLEAN,
    profile TEXT,
    profile_medium TEXT,
    sex TEXT,
    state TEXT,
    summit BOOLEAN,
    updated_at TIMESTAMP,
    username TEXT,
    weight TEXT,

    -- gear fields
    gear_name TEXT,
    brand_name TEXT,
    model_name TEXT,
    gear_distance BIGINT
);

-- Create table daily_summary under GOLD --
CREATE TABLE IF NOT EXISTS {{ params.gold_schema }}.{{ params.daily_summary }}
(
    day DATE PRIMARY KEY,
    num_activities BIGINT NOT NULL,
    total_distance_km DOUBLE PRECISION,
    total_time_min DOUBLE PRECISION,
    avg_speed_kmh DOUBLE PRECISION,
    avg_pace DOUBLE PRECISION
);

-- Create table monthly_summary under GOLD --
CREATE TABLE IF NOT EXISTS {{ params.gold_schema }}.{{ params.monthly_summary }}
(
    year INT,
    month INT,
    total_distance_km DOUBLE PRECISION,
    num_activities BIGINT NOT NULL,
    avg_pace DOUBLE PRECISION,
    total_elevation DOUBLE PRECISION,
    PRIMARY KEY (year, month)
);

-- Create table type_summary under GOLD --
CREATE TABLE IF NOT EXISTS {{ params.gold_schema }}.{{ params.type_summary }}
(
    sport_type TEXT PRIMARY KEY,
    count BIGINT NOT NULL,
    total_distance_km DOUBLE PRECISION,
    avg_speed DOUBLE PRECISION
);

-- Create table personal_records under GOLD --
CREATE TABLE IF NOT EXISTS {{ params.gold_schema }}.{{ params.personal_records }}
(
    id SERIAL PRIMARY KEY,
    longest_distance DOUBLE PRECISION,
    max_speed DOUBLE PRECISION,
    best_pace DOUBLE PRECISION,
    max_elevation DOUBLE PRECISION
);

CREATE INDEX IF NOT EXISTS idx_activities_athlete_id ON {{ params.bronze_schema }}.{{ params.activities }}(athlete_id);
CREATE INDEX IF NOT EXISTS idx_activities_gear_id ON {{ params.bronze_schema }}.{{ params.activities }}(gear_id);
CREATE INDEX IF NOT EXISTS idx_silver_day ON {{ params.silver_schema }}.{{ params.activities_enriched }}(day);
CREATE INDEX IF NOT EXISTS idx_silver_year_month ON {{ params.silver_schema }}.{{ params.activities_enriched }}(year, month);