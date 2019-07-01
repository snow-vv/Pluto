-- Deploy medivh:2017_07_27_relations to mysql

BEGIN;
CREATE TABLE `InitRelation` (
  `id` int(11) AUTO_INCREMENT NOT NULL  PRIMARY KEY,
  `src` varchar(32) NOT NULL,
  `target` varchar(32) NOT NULL,
  `weight` int(11) NOT NULL
);

COMMIT;
