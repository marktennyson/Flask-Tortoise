-- upgrade --
ALTER TABLE "users" DROP COLUMN "name";
-- downgrade --
ALTER TABLE "users" ADD "name" VARCHAR(20);
