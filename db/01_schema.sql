-- Public charging stations. SYNTHETIC DATA — plausible, but invented.
CREATE TABLE IF NOT EXISTS stations (
    id               SERIAL PRIMARY KEY,
    name             TEXT         NOT NULL,
    operator         TEXT         NOT NULL,
    city             TEXT         NOT NULL,
    state            TEXT         NOT NULL,
    connector_type   TEXT         NOT NULL,   -- CCS2 | Type2 | CHAdeMO
    power_kw         NUMERIC(6,1) NOT NULL,
    connectors       INTEGER      NOT NULL,
    status           TEXT         NOT NULL,   -- live | maintenance | planned
    price_per_kwh    NUMERIC(6,2),
    commissioned_on  DATE
);

CREATE INDEX IF NOT EXISTS stations_city_idx ON stations (city);
