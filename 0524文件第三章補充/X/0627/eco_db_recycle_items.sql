
DROP TABLE IF EXISTS `recycle_items`;


CREATE TABLE `recycle_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `points_required` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


LOCK TABLES `recycle_items` WRITE;
/*!40000 ALTER TABLE `recycle_items` DISABLE KEYS */;
INSERT INTO `recycle_items` VALUES (1,'塑膠瓶',15),(2,'金屬罐',25),(3,'金屬罐',25),(4,'紙類',30),(5,'紙容器',25),(6,'玻璃瓶',40),(7,'塑膠袋',20),(8,'環保杯',35),(9,'玻璃杯',30),(10,'塑膠袋',20);
/*!40000 ALTER TABLE `recycle_items` ENABLE KEYS */;
UNLOCK TABLES;
