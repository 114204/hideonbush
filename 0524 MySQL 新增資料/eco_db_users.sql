-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: eco_db
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `points` int DEFAULT '100',
  `address` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `birthday` date DEFAULT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'testuser','hashed_password_here',100,NULL,NULL,NULL,NULL),(2,'eva','pbkdf2:sha256:260000$FTUs5SOMbnXosCe1$edb63c296405a7fcd99c65060cb8478946e89ff5653f518a59acbd622a177c1f',100,NULL,NULL,NULL,NULL),(4,'wei','pbkdf2:sha256:260000$HJNQp0Gn404XgleX$7a7d8e872b9459fcc128a2a902b9f09520455f69a58f1d06f196b1cdfe0f176e',100,NULL,NULL,NULL,NULL),(6,'alicechen','pass1234',100,'台北市大安區仁愛路100號','1998-05-21','alice.chen@example.com','0912345678'),(7,'brianlin','hello5678',100,'新北市板橋區文化路200號','1995-12-03','brian.lin@example.com','0923456789'),(8,'cindywang','abc9999',100,'桃園市中壢區中央西路10號','2000-01-15','cindy.wang@example.com','0934567890'),(9,'davidwu','qwerty88',100,'台中市西屯區台灣大道三段300號','1992-07-09','david.wu@example.com','0966123456'),(10,'emilyliu','test5678',100,'高雄市左營區自由三路90號','1997-03-30','emily.liu@example.com','0955123456'),(11,'frankchou','pass9999',100,'基隆市仁愛區愛三路8號','1994-10-12','frank.chou@example.com','0987654321'),(12,'gracehuang','iloveu11',100,'新竹市東區光復路二段25號','1999-11-11','grace.huang@example.com','0911222333'),(13,'henrykao','hello000',100,'台南市中西區民生路一段66號','1993-06-05','henry.kao@example.com','0933111222'),(14,'ivytsai','mypwd333',100,'宜蘭縣羅東鎮中山路88號','2001-08-17','ivy.tsai@example.com','0977555666'),(15,'jasonlee','passpass',100,'花蓮縣花蓮市中正路5號','1990-09-23','jason.lee@example.com','0966888999'),(16,'001','pbkdf2:sha256:260000$VCunSTVIE7okXcAC$c1636d54872848fd88372f5f4612c7dfeb99bccccc1c41548e72e33c85aee405',100,'kh','2025-04-15','evaluyiwei@gmail.com','0932899099'),(17,'002','pbkdf2:sha256:260000$8iEQG6BX0u4aag5F$7fc8b25ab7d860277a8f475eb940db982877a526ef61cd6bda9b000112fa3c34',100,'kh','2025-04-03','11336024@ntub.edu.tw','0932899099'),(18,'003','$2b$12$yfS.PrfW14WADJ0fKT5FMu/8m8Ebj9gY9fKrDncHDLTsmxBnmoUKG',100,'kh','2025-04-08','10856034@ntub.edu.tw','0932899099'),(19,'004','$2b$12$4102kfbnGe4.n34ow7ZIUOzYlYTKoUcyQWmfKdjs8Zol4BCiJsirq',100,'kh','2025-04-17','eva@gmail.com','0932899099'),(20,'005','$2b$12$Y6Hkx616qdEDkWAjyhfO7OvEspwHY1R.fpQ72WTkVp5ghtvummqYW',100,'kh','2025-04-11','wei@gmail.com','0932899099'),(21,'006','$2b$12$1Sj1AF3Yy1kCMBGaWbpyseuaMxjzaOxsu/yTp7TzOQn/HPV1RZQ6a',100,'kkh','2025-04-15','bbyw@gmail.com','0932899099'),(22,'007','$2b$12$gKTfJYv8lyYuZBiJPfDUYuKcbw8Y/osv48s6n.u1dVIFCNgkKJbue',100,'kkhh','2025-04-05','007@gmail.com','0932899099'),(23,'008','$2b$12$KMjSu4YYaKExh5fD7fgRu.5cNZFYp2l/QubVKzeLywbGO4nC8GkCe',100,'kh','2025-04-09','008@gmail.com','0932899099');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-24 22:04:53
