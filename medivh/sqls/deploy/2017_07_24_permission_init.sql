-- Deploy medivh:2017_07_24_permission_init to mysql

BEGIN;
--
-- Create model Group
--
CREATE TABLE `permission_group` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `name` varchar(30) NOT NULL);
--
-- Create model Permission
--
CREATE TABLE `permission_permission` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `code` varchar(30) NOT NULL, `description` varchar(200) NOT NULL);
--
-- Add field permissions to group
--
CREATE TABLE `permission_group_permissions` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `group_id` integer NOT NULL, `permission_id` integer NOT NULL);
--
-- Add field users to group
--
CREATE TABLE `permission_group_users` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `group_id` integer NOT NULL, `user_id` integer NOT NULL);
ALTER TABLE `permission_group_permissions` ADD CONSTRAINT `permission_group_per_group_id_f776f1d1_fk_permissio` FOREIGN KEY (`group_id`) REFERENCES `permission_group` (`id`);
ALTER TABLE `permission_group_permissions` ADD CONSTRAINT `permission_group_per_permission_id_11ef3af7_fk_permissio` FOREIGN KEY (`permission_id`) REFERENCES `permission_permission` (`id`);
ALTER TABLE `permission_group_permissions` ADD CONSTRAINT `permission_group_permiss_group_id_permission_id_765b8da8_uniq` UNIQUE (`group_id`, `permission_id`);
ALTER TABLE `permission_group_users` ADD CONSTRAINT `permission_group_users_group_id_43f00628_fk_permission_group_id` FOREIGN KEY (`group_id`) REFERENCES `permission_group` (`id`);
ALTER TABLE `permission_group_users` ADD CONSTRAINT `permission_group_users_user_id_3cac75a4_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `permission_group_users` ADD CONSTRAINT `permission_group_users_group_id_user_id_79315f32_uniq` UNIQUE (`group_id`, `user_id`);

CREATE TABLE `permission_group_services` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `group_id` integer NOT NULL, `service_id` integer NOT NULL);
ALTER TABLE `permission_group_services` ADD CONSTRAINT `permission_group_ser_group_id_93d2c3aa_fk_permissio` FOREIGN KEY (`group_id`) REFERENCES `permission_group` (`id`);
ALTER TABLE `permission_group_services` ADD CONSTRAINT `permission_group_ser_service_id_54aa9945_fk_golive_se` FOREIGN KEY (`service_id`) REFERENCES `golive_service` (`id`);
ALTER TABLE `permission_group_services` ADD CONSTRAINT `permission_group_services_group_id_service_id_2d109f76_uniq` UNIQUE (`group_id`, `service_id`);
COMMIT;