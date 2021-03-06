-- upgrade --
CREATE TABLE IF NOT EXISTS "users" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "status" VARCHAR(20) NOT NULL
);
CREATE TABLE IF NOT EXISTS "workers" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "status" VARCHAR(20) NOT NULL
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSON NOT NULL
);
