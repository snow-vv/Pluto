-- Deploy medivh:2017_11_14_add_rds_table to mysql

BEGIN;

CREATE TABLE `cmdb_rds` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `instance_id` varchar(30) NOT NULL, `region_id` varchar(50) NOT NULL, `description` varchar(200) NOT NULL, `status` varchar(100) NOT NULL);

COMMIT;
