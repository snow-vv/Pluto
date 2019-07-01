-- Verify medivh:2018_09_11_add_dtabrules_table on mysql

BEGIN;

-- XXX Add verifications here.
SELECT * FROM `golive_dtabrules` LIMIT 1;

ROLLBACK;
