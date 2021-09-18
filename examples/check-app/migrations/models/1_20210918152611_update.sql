-- upgrade --
CREATE TABLE IF NOT EXISTS "coworker" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "rltn_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
-- downgrade --
DROP TABLE IF EXISTS "coworker";
