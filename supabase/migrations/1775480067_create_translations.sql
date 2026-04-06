CREATE TABLE IF NOT EXISTS translations (
    id          SERIAL      PRIMARY KEY,
    source_text TEXT        NOT NULL,
    translation TEXT        NOT NULL,
    created_at  TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);
