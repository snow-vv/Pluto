-- Deploy medivh:2018_09_11_add_dtabrules_table to mysql

BEGIN;

-- XXX Add DDLs here.
CREATE TABLE `golive_dtabrules` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `name` varchar(100) NOT NULL, `rule` longtext NOT NULL);

COMMIT;
