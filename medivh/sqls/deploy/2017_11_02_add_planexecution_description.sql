-- Deploy medivh:2017_11_02_add_planexecution_description to mysql

BEGIN;

ALTER TABLE `golive_planexecution`
ADD COLUMN `description` VARCHAR(500) DEFAULT '';

COMMIT;
