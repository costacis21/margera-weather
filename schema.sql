CREATE TABLE locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE forecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL,
    forecast_date DATE NOT NULL,
    t_2m DECIMAL(5,2),
    precip_1h DECIMAL(5,2),
    prob_precip_1h DECIMAL(5,2),
    wind_speed_10m DECIMAL(5,2),
    relative_humidity_2m DECIMAL(5,2),
    frost_depth DECIMAL(5,2),
    sunshine_duration_1h DECIMAL(5,2),
    global_rad DECIMAL(6,2),
    FOREIGN KEY (location_id) REFERENCES locations(id),
    -- composite index to enforce unique forecasts per location, date
    UNIQUE (location_id, forecast_date)
);

-- index for common query patterns
CREATE INDEX idx_forecasts_location_date ON forecasts(location_id, forecast_date);
