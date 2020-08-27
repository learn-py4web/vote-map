CREATE TABLE `auth_user` (
    `id` int(11) AUTO_INCREMENT NOT NULL,
    `username` varchar(512) UNIQUE,
    `email` varchar(512) UNIQUE,
    `password` varchar(512),
    `first_name` varchar(512),
    `last_name` varchar(512),
    `sso_id` varchar(512),
    `action_token` varchar(512),
    `last_password_change` timestamp,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `auth_user_tag_groups` (
    `id` int(11) AUTO_INCREMENT NOT NULL,
    `path` varchar(512),
    `record_id` int(11),
    PRIMARY KEY (`id`)  ,
    CONSTRAINT `record_id_fk` FOREIGN KEY (`record_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `location` (
    `id` int(11) AUTO_INCREMENT NOT NULL,
    `is_deleted` varchar(1) DEFAULT NULL,
    `lat` double,
    `lng` double,
    `address_lat` double,
    `address_lng` double,
    `square10` varchar(32) DEFAULT NULL,
    `name` varchar(255) DEFAULT NULL,
    `loc_type` varchar(255) DEFAULT NULL,
    `type_other` varchar(255) DEFAULT NULL,
    `date_open` date DEFAULT NULL,
    `date_close` date DEFAULT NULL,
    `time_open` time DEFAULT NULL,
    `time_close` time DEFAULT NULL,
    `address` text,
    `rules` text,
    `date_created` datetime DEFAULT NULL,
    `date_updated` datetime DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `square10__idx` (`square10`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `location_history` (
    `id` int(11) AUTO_INCREMENT NOT NULL,
    `location_id` int(11) DEFAULT NULL,
    `is_deleted` varchar(1) DEFAULT NULL,
    `author` varchar(255) DEFAULT NULL,
    `lat` double,
    `lng` double,
    `address_lat` double,
    `address_lng` double,
    `square10` varchar(32) DEFAULT NULL,
    `name` varchar(255) DEFAULT NULL,
    `loc_type` varchar(255) DEFAULT NULL,
    `type_other` varchar(255) DEFAULT NULL,
    `date_open` date DEFAULT NULL,
    `date_close` date DEFAULT NULL,
    `time_open` time DEFAULT NULL,
    `time_close` time DEFAULT NULL,
    `address` text,
    `rules` text,
    `max_zoom` int DEFAULT NULL,
    `edit_time` int DEFAULT NULL,
    `timestamp` datetime DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `location_id_timestamp__idx` (`location_id`, `timestamp`),
    CONSTRAINT `location_id_fk` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`) ON DELETE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `vote` (
    `id` int(11) AUTO_INCREMENT NOT NULL,
    `location_history_id` int(11) DEFAULT NULL,
    `author` varchar(255) DEFAULT NULL,
    `timestamp` datetime DEFAULT NULL,
    `max_zoom` int DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `location_history_id_author__idx` (`location_history_id`, `author`),
    CONSTRAINT `location_history_id_fk` FOREIGN KEY (`location_history_id`) REFERENCES `location_history` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `zipcode` (
    `id` int(11) AUTO_INCREMENT NOT NULL,
    `zipcode` varchar(16),
    `lat` double,
    `lng` double,
    PRIMARY KEY (`id`),
    KEY `zipcode__idx` (`zipcode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;