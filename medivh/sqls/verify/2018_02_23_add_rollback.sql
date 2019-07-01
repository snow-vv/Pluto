-- Verify medivh:2018_02_23_add_rollback on mysql

BEGIN;

-- XXX Add verifications here.

SELECT 1 FROM `golive_servicecommitrecords`;

ROLLBACK;
