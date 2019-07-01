-- Deploy medivh:2017_11_16_add_slow_log_dingding_column_to_rds_table to mysql

BEGIN;

--
-- Add field slow_log_dingding to rds
--
ALTER TABLE `cmdb_rds` ADD COLUMN `slow_log_dingding` varchar(200) DEFAULT '' NOT NULL;
ALTER TABLE `cmdb_rds` ALTER COLUMN `slow_log_dingding` DROP DEFAULT;

COMMIT;
