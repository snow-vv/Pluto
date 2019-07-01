-- Revert medivh:2018_02_23_add_rollback from mysql

BEGIN;

-- XXX Add DDLs here.

DROP TABLE `golive_servicecommitrecords`;

COMMIT;
