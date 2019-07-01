BEGIN;
CREATE TABLE `django_content_type` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `name` varchar(100) NOT NULL, `app_label` varchar(100) NOT NULL, `model` varchar(100) NOT NULL);
ALTER TABLE `django_content_type` ADD CONSTRAINT `django_content_type_app_label_24a768bd05457a93_uniq` UNIQUE (`app_label`, `model`);
CREATE TABLE `auth_permission` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `name` varchar(50) NOT NULL, `content_type_id` integer NOT NULL, `codename` varchar(100) NOT NULL, UNIQUE (`content_type_id`, `codename`));
CREATE TABLE `auth_group` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `name` varchar(80) NOT NULL UNIQUE);
CREATE TABLE `auth_group_permissions` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `group_id` integer NOT NULL, `permission_id` integer NOT NULL, UNIQUE (`group_id`, `permission_id`));
CREATE TABLE `auth_user` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `password` varchar(128) NOT NULL, `last_login` datetime(6) NOT NULL, `is_superuser` bool NOT NULL, `username` varchar(30) NOT NULL UNIQUE, `first_name` varchar(30) NOT NULL, `last_name` varchar(30) NOT NULL, `email` varchar(75) NOT NULL, `is_staff` bool NOT NULL, `is_active` bool NOT NULL, `date_joined` datetime(6) NOT NULL);
CREATE TABLE `auth_user_groups` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `user_id` integer NOT NULL, `group_id` integer NOT NULL, UNIQUE (`user_id`, `group_id`));
CREATE TABLE `auth_user_user_permissions` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `user_id` integer NOT NULL, `permission_id` integer NOT NULL, UNIQUE (`user_id`, `permission_id`));
ALTER TABLE `auth_permission` ADD CONSTRAINT `auth__content_type_id_73051f9e78aafe35_fk_django_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);
ALTER TABLE `auth_group_permissions` ADD CONSTRAINT `auth_group_permission_group_id_44da11c39e881854_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);
ALTER TABLE `auth_group_permissions` ADD CONSTRAINT `auth_group_p_permission_id_d04bc12f55f2d29_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`);
ALTER TABLE `auth_user_groups` ADD CONSTRAINT `auth_user_groups_user_id_18c69ef6b51c4571_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `auth_user_groups` ADD CONSTRAINT `auth_user_groups_group_id_13235696326612f_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);
ALTER TABLE `auth_user_user_permissions` ADD CONSTRAINT `auth_user_user_permissi_user_id_1d68d06e7bd8bf5a_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `auth_user_user_permissions` ADD CONSTRAINT `auth_user_u_permission_id_461400ce3dd64adb_fk_auth_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`);
CREATE TABLE `cmdb_ecs` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(100) NOT NULL,
    `ip` varchar(100) NOT NULL UNIQUE,
    `instance_id` varchar(30) UNIQUE,
    `cpu` integer NOT NULL,
    `memory` integer NOT NULL,
    `description` varchar(200) NOT NULL,
    `public_ip` varchar(30),
    `created_time` datetime(6)
)
;
CREATE TABLE `cmdb_instancetype` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `code` varchar(100) NOT NULL,
    `cpu_core_count` integer NOT NULL,
    `memory_size` integer NOT NULL,
    `cloud_type` integer NOT NULL
)
;
CREATE TABLE `cmdb_slb` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `instance_id` varchar(30) NOT NULL,
    `name` varchar(100) NOT NULL,
    `ip` varchar(100) NOT NULL UNIQUE,
    `description` varchar(200) NOT NULL
)
;
CREATE TABLE `golive_function` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(100) NOT NULL
)
;
CREATE TABLE `golive_task` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `function_id` integer NOT NULL,
    `params_json` longtext NOT NULL,
    `order` integer NOT NULL
)
;
ALTER TABLE `golive_task` ADD CONSTRAINT `function_id_refs_id_934ce1c4` FOREIGN KEY (`function_id`) REFERENCES `golive_function` (`id`);
CREATE TABLE `golive_gitrepo` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(100) NOT NULL,
    `repo` varchar(100) NOT NULL,
    `requirements_path` varchar(100) NOT NULL,
    `manage_path` varchar(100) NOT NULL
)
;
CREATE TABLE `golive_service_ecses` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `service_id` integer NOT NULL,
    `ecs_id` integer NOT NULL,
    UNIQUE (`service_id`, `ecs_id`)
)
;
ALTER TABLE `golive_service_ecses` ADD CONSTRAINT `ecs_id_refs_id_d30afa16` FOREIGN KEY (`ecs_id`) REFERENCES `cmdb_ecs` (`id`);
CREATE TABLE `golive_service_slbs` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `service_id` integer NOT NULL,
    `slb_id` integer NOT NULL,
    UNIQUE (`service_id`, `slb_id`)
)
;
ALTER TABLE `golive_service_slbs` ADD CONSTRAINT `slb_id_refs_id_b04f9ebf` FOREIGN KEY (`slb_id`) REFERENCES `cmdb_slb` (`id`);
CREATE TABLE `golive_service` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(100) NOT NULL,
    `app_dir` varchar(100) NOT NULL,
    `static_dir` varchar(100),
    `virtualenv_dir` varchar(100) NOT NULL,
    `process_control` integer NOT NULL,
    `process_control_name` varchar(100) NOT NULL,
    `git_repo_id` integer NOT NULL
)
;
ALTER TABLE `golive_service` ADD CONSTRAINT `git_repo_id_refs_id_cbbbc7c2` FOREIGN KEY (`git_repo_id`) REFERENCES `golive_gitrepo` (`id`);
ALTER TABLE `golive_service_ecses` ADD CONSTRAINT `service_id_refs_id_331b94ff` FOREIGN KEY (`service_id`) REFERENCES `golive_service` (`id`);
ALTER TABLE `golive_service_slbs` ADD CONSTRAINT `service_id_refs_id_49778ee7` FOREIGN KEY (`service_id`) REFERENCES `golive_service` (`id`);
CREATE TABLE `golive_serviceexecutioninfo_ecses` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `serviceexecutioninfo_id` integer NOT NULL,
    `ecs_id` integer NOT NULL,
    UNIQUE (`serviceexecutioninfo_id`, `ecs_id`)
)
;
ALTER TABLE `golive_serviceexecutioninfo_ecses` ADD CONSTRAINT `ecs_id_refs_id_0d1b7438` FOREIGN KEY (`ecs_id`) REFERENCES `cmdb_ecs` (`id`);
CREATE TABLE `golive_serviceexecutioninfo` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `service_id` integer NOT NULL,
    `type` integer NOT NULL,
    UNIQUE (`service_id`, `type`)
)
;
ALTER TABLE `golive_serviceexecutioninfo` ADD CONSTRAINT `service_id_refs_id_a0b4bb14` FOREIGN KEY (`service_id`) REFERENCES `golive_service` (`id`);
ALTER TABLE `golive_serviceexecutioninfo_ecses` ADD CONSTRAINT `serviceexecutioninfo_id_refs_id_7eb5b657` FOREIGN KEY (`serviceexecutioninfo_id`) REFERENCES `golive_serviceexecutioninfo` (`id`);
CREATE TABLE `golive_plan` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `description` varchar(100) NOT NULL,
    `created_time` datetime(6) NOT NULL,
    `golive_expected_time` datetime(6),
    `tasks` longtext NOT NULL,
    `creator_id` integer NOT NULL,
    `assignee_id` integer,
    `status` integer NOT NULL,
    `jira_id` varchar(30),
    `notes` longtext NOT NULL
)
;
ALTER TABLE `golive_plan` ADD CONSTRAINT `creator_id_refs_id_b5a0d2cf` FOREIGN KEY (`creator_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `golive_plan` ADD CONSTRAINT `assignee_id_refs_id_b5a0d2cf` FOREIGN KEY (`assignee_id`) REFERENCES `auth_user` (`id`);
CREATE TABLE `golive_planstage_tasks` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `planstage_id` integer NOT NULL,
    `task_id` integer NOT NULL,
    UNIQUE (`planstage_id`, `task_id`)
)
;
ALTER TABLE `golive_planstage_tasks` ADD CONSTRAINT `task_id_refs_id_4dad2a02` FOREIGN KEY (`task_id`) REFERENCES `golive_task` (`id`);
CREATE TABLE `golive_planstage` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `plan_id` integer NOT NULL,
    `service_id` integer NOT NULL,
    `order` integer NOT NULL
)
;
ALTER TABLE `golive_planstage` ADD CONSTRAINT `plan_id_refs_id_7e61fdb5` FOREIGN KEY (`plan_id`) REFERENCES `golive_plan` (`id`);
ALTER TABLE `golive_planstage` ADD CONSTRAINT `service_id_refs_id_1602d350` FOREIGN KEY (`service_id`) REFERENCES `golive_service` (`id`);
ALTER TABLE `golive_planstage_tasks` ADD CONSTRAINT `planstage_id_refs_id_61182c6c` FOREIGN KEY (`planstage_id`) REFERENCES `golive_planstage` (`id`);
CREATE TABLE `golive_plantemplate` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(100) NOT NULL,
    `tasks` longtext NOT NULL,
    `creator_id` integer NOT NULL,
    `created_time` datetime(6) NOT NULL,
    `last_modify_time` datetime(6) NOT NULL
)
;
ALTER TABLE `golive_plantemplate` ADD CONSTRAINT `creator_id_refs_id_4a208093` FOREIGN KEY (`creator_id`) REFERENCES `auth_user` (`id`);
CREATE TABLE `golive_planstatuschangelog` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `plan_id` integer NOT NULL,
    `user_id` integer,
    `source_status` integer NOT NULL,
    `target_status` integer NOT NULL,
    `action_time` datetime(6) NOT NULL
)
;
ALTER TABLE `golive_planstatuschangelog` ADD CONSTRAINT `user_id_refs_id_7a146f8e` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `golive_planstatuschangelog` ADD CONSTRAINT `plan_id_refs_id_e5039776` FOREIGN KEY (`plan_id`) REFERENCES `golive_plan` (`id`);
CREATE TABLE `golive_planexecution` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `plan_id` integer,
    `user_id` integer NOT NULL,
    `start_time` datetime(6),
    `end_time` datetime(6)
)
;
ALTER TABLE `golive_planexecution` ADD CONSTRAINT `user_id_refs_id_e62e0bb2` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `golive_planexecution` ADD CONSTRAINT `plan_id_refs_id_71cb3fa0` FOREIGN KEY (`plan_id`) REFERENCES `golive_plan` (`id`);
CREATE TABLE `golive_planstageexecution` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `execution_id` integer NOT NULL,
    `plan_stage_id` integer,
    `service_execution_info_id` integer NOT NULL,
    `hosts` longtext NOT NULL,
    `start_time` datetime(6) NOT NULL,
    `end_time` datetime(6),
    `status` integer NOT NULL,
    `tasks` longtext NOT NULL
)
;
ALTER TABLE `golive_planstageexecution` ADD CONSTRAINT `service_execution_info_id_refs_id_75b58da4` FOREIGN KEY (`service_execution_info_id`) REFERENCES `golive_serviceexecutioninfo` (`id`);
ALTER TABLE `golive_planstageexecution` ADD CONSTRAINT `plan_stage_id_refs_id_15c6a5ad` FOREIGN KEY (`plan_stage_id`) REFERENCES `golive_planstage` (`id`);
ALTER TABLE `golive_planstageexecution` ADD CONSTRAINT `execution_id_refs_id_26198f8c` FOREIGN KEY (`execution_id`) REFERENCES `golive_planexecution` (`id`);
CREATE TABLE `golive_planstageexecutionsubtask` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `run_time` datetime(6) NOT NULL,
    `plan_stage_execution_id` integer NOT NULL,
    `is_success` bool NOT NULL,
    `result_json` longtext NOT NULL,
    `description` varchar(500) NOT NULL,
    `host` varchar(100) NOT NULL
)
;
ALTER TABLE `golive_planstageexecutionsubtask` ADD CONSTRAINT `plan_stage_execution_id_refs_id_2f28ce63` FOREIGN KEY (`plan_stage_execution_id`) REFERENCES `golive_planstageexecution` (`id`);
CREATE TABLE `golive_grey_services` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `grey_id` integer NOT NULL,
    `service_id` integer NOT NULL,
    UNIQUE (`grey_id`, `service_id`)
)
;
ALTER TABLE `golive_grey_services` ADD CONSTRAINT `service_id_refs_id_cb96570b` FOREIGN KEY (`service_id`) REFERENCES `golive_service` (`id`);
CREATE TABLE `golive_grey_ecses` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `grey_id` integer NOT NULL,
    `ecs_id` integer NOT NULL,
    UNIQUE (`grey_id`, `ecs_id`)
)
;
ALTER TABLE `golive_grey_ecses` ADD CONSTRAINT `ecs_id_refs_id_f2870dc8` FOREIGN KEY (`ecs_id`) REFERENCES `cmdb_ecs` (`id`);
CREATE TABLE `golive_grey_executions` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `grey_id` integer NOT NULL,
    `planexecution_id` integer NOT NULL,
    UNIQUE (`grey_id`, `planexecution_id`)
)
;
ALTER TABLE `golive_grey_executions` ADD CONSTRAINT `planexecution_id_refs_id_553e3382` FOREIGN KEY (`planexecution_id`) REFERENCES `golive_planexecution` (`id`);
CREATE TABLE `golive_grey` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(30) NOT NULL,
    `route_path` varchar(300) NOT NULL,
    `description` longtext NOT NULL,
    `status` integer NOT NULL
)
;
ALTER TABLE `golive_grey_services` ADD CONSTRAINT `grey_id_refs_id_ce0e7c39` FOREIGN KEY (`grey_id`) REFERENCES `golive_grey` (`id`);
ALTER TABLE `golive_grey_ecses` ADD CONSTRAINT `grey_id_refs_id_6edd9f02` FOREIGN KEY (`grey_id`) REFERENCES `golive_grey` (`id`);
ALTER TABLE `golive_grey_executions` ADD CONSTRAINT `grey_id_refs_id_7a7ee9d9` FOREIGN KEY (`grey_id`) REFERENCES `golive_grey` (`id`);
CREATE INDEX `golive_task_aecb9bce` ON `golive_task` (`function_id`);
CREATE INDEX `golive_service_ecses_91a0ac17` ON `golive_service_ecses` (`service_id`);
CREATE INDEX `golive_service_ecses_cefba381` ON `golive_service_ecses` (`ecs_id`);
CREATE INDEX `golive_service_slbs_91a0ac17` ON `golive_service_slbs` (`service_id`);
CREATE INDEX `golive_service_slbs_166305c5` ON `golive_service_slbs` (`slb_id`);
CREATE INDEX `golive_service_1a588a00` ON `golive_service` (`git_repo_id`);
CREATE INDEX `golive_serviceexecutioninfo_ecses_ae63c61c` ON `golive_serviceexecutioninfo_ecses` (`serviceexecutioninfo_id`);
CREATE INDEX `golive_serviceexecutioninfo_ecses_cefba381` ON `golive_serviceexecutioninfo_ecses` (`ecs_id`);
CREATE INDEX `golive_serviceexecutioninfo_91a0ac17` ON `golive_serviceexecutioninfo` (`service_id`);
CREATE INDEX `golive_plan_ad376f8d` ON `golive_plan` (`creator_id`);
CREATE INDEX `golive_plan_98516953` ON `golive_plan` (`assignee_id`);
CREATE INDEX `golive_planstage_tasks_648f7f6d` ON `golive_planstage_tasks` (`planstage_id`);
CREATE INDEX `golive_planstage_tasks_ef96c3b8` ON `golive_planstage_tasks` (`task_id`);
CREATE INDEX `golive_planstage_188ba6de` ON `golive_planstage` (`plan_id`);
CREATE INDEX `golive_planstage_91a0ac17` ON `golive_planstage` (`service_id`);
CREATE INDEX `golive_plantemplate_ad376f8d` ON `golive_plantemplate` (`creator_id`);
CREATE INDEX `golive_planstatuschangelog_188ba6de` ON `golive_planstatuschangelog` (`plan_id`);
CREATE INDEX `golive_planstatuschangelog_6340c63c` ON `golive_planstatuschangelog` (`user_id`);
CREATE INDEX `golive_planexecution_188ba6de` ON `golive_planexecution` (`plan_id`);
CREATE INDEX `golive_planexecution_6340c63c` ON `golive_planexecution` (`user_id`);
CREATE INDEX `golive_planstageexecution_042fe192` ON `golive_planstageexecution` (`execution_id`);
CREATE INDEX `golive_planstageexecution_538551d6` ON `golive_planstageexecution` (`plan_stage_id`);
CREATE INDEX `golive_planstageexecution_ba532124` ON `golive_planstageexecution` (`service_execution_info_id`);
CREATE INDEX `golive_planstageexecutionsubtask_255fa9eb` ON `golive_planstageexecutionsubtask` (`plan_stage_execution_id`);
CREATE INDEX `golive_grey_services_f399877c` ON `golive_grey_services` (`grey_id`);
CREATE INDEX `golive_grey_services_91a0ac17` ON `golive_grey_services` (`service_id`);
CREATE INDEX `golive_grey_ecses_f399877c` ON `golive_grey_ecses` (`grey_id`);
CREATE INDEX `golive_grey_ecses_cefba381` ON `golive_grey_ecses` (`ecs_id`);
CREATE INDEX `golive_grey_executions_f399877c` ON `golive_grey_executions` (`grey_id`);
CREATE INDEX `golive_grey_executions_8f5a5e8d` ON `golive_grey_executions` (`planexecution_id`);
CREATE TABLE `cmdb_userextra` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `phone` varchar(13) NULL, `user_id` integer NOT NULL UNIQUE);
COMMIT;