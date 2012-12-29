CREATE TABLE `metric` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `key` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `value` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `metric_986cbc25` (`date`),
  KEY `metric_45544485` (`key`),
  KEY `metric_52094d6e` (`name`),
  KEY `metric_40858fbd` (`value`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
