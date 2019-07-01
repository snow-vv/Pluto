-- Deploy medivh:2018_02_23_add_rollback to mysql

BEGIN;

-- XXX Add DDLs here.

CREATE TABLE `golive_servicecommitrecords`(
  `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
  `commit_id` varchar(64) NOT NULL,
  `ctime` datetime(6) NOT NULL,
  `plan_id` integer NOT NULL,
  `service_id` integer NOT NULL
);

ALTER TABLE `golive_servicecommitrecords` ADD CONSTRAINT `golive_servicecommit_service_id_d9a57d8a_fk_golive_se` FOREIGN KEY (`service_id`) REFERENCES `golive_service` (`id`);
ALTER TABLE `golive_servicecommitrecords` ADD CONSTRAINT `golive_servicecommitrecords_plan_id_b1a8277e_fk_golive_plan_id` FOREIGN KEY (`plan_id`) REFERENCES `golive_plan` (`id`);


COMMIT;
