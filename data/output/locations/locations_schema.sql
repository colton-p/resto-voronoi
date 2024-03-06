CREATE TABLE locations(
    id INTEGER PRIMARY KEY,
    tag TEXT,
    store_id TEXT,
    name TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    lat REAL,
    lon REAL
);
CREATE UNIQUE INDEX tag_store_id ON locations(tag, store_id);
