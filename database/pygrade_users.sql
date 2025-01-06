-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: pygrade
-- ------------------------------------------------------
-- Server version	8.0.40

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
  `full_name` varchar(100) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('faculty','student') NOT NULL,
  `student_id` varchar(20) DEFAULT NULL,
  `department` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `username_2` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (51,'Kenneth Viray','kennethviray@psu.edu.ph','scrypt:32768:8:1$Jf0dpdvOQnJpmMwe$762728aaa45639ba77754c5b7f5f00fc5100542b9b64ca0a431c1681639525a451994a1bf889db2fee3cab5f7303b3e4af4da944d6939caba4905671153d05c9','faculty',NULL,'Computer Engineering Department'),(52,'Reamlyx Lachica','reamlyxlachica@psu.edu.ph','scrypt:32768:8:1$z0jq466hySKUNbmL$49ab66648e2c03870cdf15137ede0e6151ec0c3ade29d950bb02a5c19f7a0dc0823f55912197e14d696e63f289af45fa66fae87f8fff7a722e3ad3280f59a309','faculty',NULL,'Computer Engineering Department'),(53,'Victor Sherwin Galamgam','victorsherwingalamgam@psu.edu.ph','scrypt:32768:8:1$gEHAVIW2wp8mTBgX$b995b3a7385489ec03ac43ff3404026d119b2028ebee5b0dbf6e387a50f22a91ddb3cee4179a5bbb88372100a85952f75b368d893b20eeef1679c8e718afb172','faculty',NULL,'Computer Engineering Department'),(54,'Roderick Calguio','roderickcalaguio@psu.edu.ph','scrypt:32768:8:1$SbYaGE4uO0vk3s17$0d169ff96042a9c7b57f67dbb1ec8f5be4a08ccdaf0e9f3dda3ae92ffbd47691e78cf57402bbd7d1c690e264996f793cd022cd25d2bcd695a9f40bbdcaff4b6c','faculty',NULL,'Computer Engineering Department'),(55,'Kenneth Lopez','kennethlopez@psu.edu.ph','scrypt:32768:8:1$WXbwIPyL8E0KjbLK$e347ee78a39466d1001fda4a9de8ccc8510cbd72af7961402202d91b710d345af8f1aecc2a013e16b1eda446493d57ca0500fcc92e0c9f7bff3d5839b84d874b','faculty',NULL,'Computer Engineering Department'),(56,'Koji Ken Dela Cruz','kojikendelacruz@psu.edu.ph','scrypt:32768:8:1$f6butzQYPvTbZImt$509ce0b4b4cad9afafc0a6fa5821a8cf9dc5196b74f77253bac2e9399e0684666699db118c7238f5da0de9e258120eddb1422ba7f5f87f225a8beeeef72a3b69','student','UR-CpE-001',NULL),(57,'Jonard Hortizuela','jonardhortizuela@psu.edu.ph','scrypt:32768:8:1$ZkGoLMrdvg2yBlRG$67dd65487c0aa4787dde52d928f29ca03ae9050c9d20a31cd93fba7447b7caa1fb1fb7a8bed90d1eccff9018a7ecc2d34e6a05359c2fef359b8e1bbd3e121934','student','UR-CpE-002',NULL),(58,'B-Jay Benjamin Locquiao','bjaybenjaminlocquiao@psu.edu.ph','scrypt:32768:8:1$670iNaOnKOwnnAyT$9d8c3cdf4b60eb309fb191dad2750b42b8ed1bfc44cc2d048e09a06b063c0f829beb5969747a6f23faba794c6cb66fbbdcc4bf677abbea1d606762840fe927b0','student','UR-CpE-003',NULL),(59,'Jearome Haruld Nicolas','jearomeharuldnicolas@psu.edu.ph','scrypt:32768:8:1$MMz0dYe4cH47fGlu$fc8c00e808c712fc846e0f93a4f3bec729aedecff16bc94a576f9fbac338323e57d9607475d5b3658b64bcffd0525eaed6014a1a49021c9fdb7cdc07815b0f1c','student','UR-CpE-004',NULL),(60,'John Rouvick De Guzman','johnrouvickdeguzman@psu.edu.ph','scrypt:32768:8:1$qTcIe5Cpxr2iGI8s$ddf1b90c66b105e39300ef0ebb2910716cd843b7eb0d1f914a62db54bb5aeebe24e8855f50d0fcdb83b12c48fae2dc2d3836edf99ac3c6f836d3600a2a817ba4','student','UR-CpE-005',NULL),(61,'Johnrei Ezra Zarasate ','johnreiezrazarasate@psu.edu.ph','scrypt:32768:8:1$ATmJdmIuGkqOY0Nr$a0b17065ff585371ae07c083c1cfa5d9e686d055056c2036162e51f314cc4716c3c93b14707c97b17c42caef771de6016f6b1b8a5e0998058d180f5fe8db4e4e','student','UR-CpE-006',NULL),(62,'Joshua Elegores','joshuaelegores@psu.edu.ph','scrypt:32768:8:1$1SN4RmXcObDdXVaF$79ea8cf45be9e1caa8aef9f36d4b2c8951920978b80b6684eec233ce1935b5ef0b46047c7545a8cc27011aa824f3557241f717ae195968804e812e3942affeb8','student','UR-CpE-007',NULL),(63,'Lance Jacob Carpiz','lancejacobcarpiz@psu.edu.ph','scrypt:32768:8:1$S7fZGEZFDXsK1LvU$2faf8c089d2656f7609921bd9776bde0fc7fd872063b9ab3c750fb5b27d5f85bfbfd6b970e9affe5e5de07bf729fd6ac7b4eb96b8747843486970ca8dcf9896c','student','UR-CpE-009',NULL),(64,'Ranelle Daracan ','renelledaracan@psu.edu.ph','scrypt:32768:8:1$nsX64YlQkJ0W8vWI$00473498f02bc7339c9a1d821720551401463e38aa0e546546a38bf1d65170bb9b9de89ce3599b82419d58442000bcc072a6f9a0f97b5ef965af331e884a18d3','student','UR-CpE-010',NULL),(65,'Sherwin Pote','sherwinpote@psu.edu.ph','scrypt:32768:8:1$3Ysgam4oaqKgfy3P$11e95d8dd6e0d17f6a3deb9076402e4e4b48f676cc98509c4ca3260f54bb12aae10c2cbb37254658ee81714bbd8af8af73a2a0784aaa26a218f51b721e5eef37','student','UR-CpE-011',NULL),(66,'Emmerson Canuel','emmersoncanuel@psu.edu.ph','scrypt:32768:8:1$olKsRgCXxd0GiPDM$9a12d72562c85c5f501e4d958cdef8f321a5277be1fc781665106d4bfe28e9c40e2aa6ce2e43a17204115367ed6cae326a20ce9bbe86409d5e0878d3882473ec','faculty',NULL,'Computer Engineering Department');
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

-- Dump completed on 2025-01-06  7:45:01
