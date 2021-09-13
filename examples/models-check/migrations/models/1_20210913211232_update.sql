-- upgrade --
CREATE TABLE IF NOT EXISTS "user" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "is_active" INT NOT NULL  DEFAULT 1
);
-- downgrade --
DROP TABLE IF EXISTS "user";
