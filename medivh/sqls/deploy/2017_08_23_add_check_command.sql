-- Deploy medivh:2017_08_23_add_check_command to mysql

BEGIN;

ALTER TABLE `golive_gitrepo`
ADD COLUMN `check_command` VARCHAR(300) DEFAULT '';

COMMIT;
