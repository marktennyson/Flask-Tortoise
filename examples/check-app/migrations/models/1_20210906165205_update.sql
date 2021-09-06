-- upgrade --
ALTER TABLE "users" ADD "name" VARCHAR(20);
-- downgrade --
ALTER TABLE "users" DROP COLUMN "name";
