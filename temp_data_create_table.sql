CREATE TABLE `temperature_data` (
  `id` int(10) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `timestamp` varchar(50) NOT NULL,
  `value_c` float NOT NULL,
  `value_f` float NOT NULL
);
