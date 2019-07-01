-- Revert medivh:2018_09_11_add_dtabrules_table from mysql

BEGIN;

-- XXX Add DDLs here.
DROP TABLE `golive_dtabrules`;

COMMIT;
