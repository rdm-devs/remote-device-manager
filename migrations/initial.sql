/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.5.2-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: kvmdb_dev
-- ------------------------------------------------------
-- Server version	11.5.2-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `auth_refresh_tokens`
--

DROP TABLE IF EXISTS `auth_refresh_tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_refresh_tokens` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `refresh_token` varchar(1000) NOT NULL,
  `expires_at` datetime NOT NULL,
  `valid` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `created_by_id` int(11) DEFAULT NULL,
  `updated_by_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_auth_refresh_tokens_id` (`id`),
  CONSTRAINT `auth_refresh_tokens_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_refresh_tokens`
--

LOCK TABLES `auth_refresh_tokens` WRITE;
/*!40000 ALTER TABLE `auth_refresh_tokens` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_refresh_tokens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device`
--

DROP TABLE IF EXISTS `device`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `is_online` tinyint(1) NOT NULL,
  `heartbeat_timestamp` datetime NOT NULL,
  `folder_id` int(11) DEFAULT NULL,
  `id_rust` varchar(255) DEFAULT NULL,
  `pass_rust` varchar(255) DEFAULT NULL,
  `last_screenshot_path` varchar(255) DEFAULT NULL,
  `entity_id` int(11) NOT NULL,
  `mac_address` varchar(17) DEFAULT NULL,
  `ip_address` varchar(15) DEFAULT NULL,
  `os_name` varchar(255) NOT NULL,
  `os_version` varchar(255) NOT NULL,
  `os_kernel_version` varchar(255) NOT NULL,
  `vendor_name` varchar(255) NOT NULL,
  `vendor_model` varchar(255) NOT NULL,
  `vendor_cores` int(11) NOT NULL,
  `vendor_ram_gb` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `created_by_id` int(11) DEFAULT NULL,
  `updated_by_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `folder_id` (`folder_id`),
  KEY `entity_id` (`entity_id`),
  KEY `ix_device_name` (`name`),
  KEY `ix_device_vendor_name` (`vendor_name`),
  KEY `ix_device_os_name` (`os_name`),
  KEY `ix_device_is_online` (`is_online`),
  KEY `ix_device_id` (`id`),
  KEY `fk_Device_updated_by_id` (`updated_by_id`),
  KEY `fk_Device_created_by_id` (`created_by_id`),
  CONSTRAINT `device_ibfk_1` FOREIGN KEY (`folder_id`) REFERENCES `folder` (`id`),
  CONSTRAINT `device_ibfk_2` FOREIGN KEY (`entity_id`) REFERENCES `entity` (`id`),
  CONSTRAINT `fk_Device_created_by_id` FOREIGN KEY (`created_by_id`) REFERENCES `user` (`id`),
  CONSTRAINT `fk_Device_updated_by_id` FOREIGN KEY (`updated_by_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device`
--

LOCK TABLES `device` WRITE;
/*!40000 ALTER TABLE `device` DISABLE KEYS */;
INSERT INTO `device` VALUES
(1,'dev1',1,'2024-09-14 21:14:40',3,NULL,NULL,NULL,13,'61:68:0C:1E:93:8F','96.119.132.44','android','10','6','samsung','galaxy tab s9',8,4,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(2,'dev2',1,'2024-09-14 21:14:40',6,NULL,NULL,NULL,14,'61:68:0C:1E:93:9F','96.119.132.45','android','10','6','lenovo','m8',8,3,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(3,'dev3',1,'2024-09-14 21:14:40',9,NULL,NULL,NULL,15,'61:68:00:1F:95:AA','96.119.132.46','android','9','5','lenovo','m8',8,3,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL);
/*!40000 ALTER TABLE `device` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `entities_and_tags`
--

DROP TABLE IF EXISTS `entities_and_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `entities_and_tags` (
  `entity_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`entity_id`,`tag_id`),
  KEY `tag_id` (`tag_id`),
  CONSTRAINT `entities_and_tags_ibfk_1` FOREIGN KEY (`entity_id`) REFERENCES `entity` (`id`) ON DELETE CASCADE,
  CONSTRAINT `entities_and_tags_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `tag` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `entities_and_tags`
--

LOCK TABLES `entities_and_tags` WRITE;
/*!40000 ALTER TABLE `entities_and_tags` DISABLE KEYS */;
INSERT INTO `entities_and_tags` VALUES
(1,1,'2024-09-14 21:14:40','2024-09-14 21:14:40'),
(1,13,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(1,16,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(2,2,'2024-09-14 21:14:40','2024-09-14 21:14:40'),
(3,3,'2024-09-14 21:14:40','2024-09-14 21:14:40'),
(3,15,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(4,4,'2024-09-14 21:14:40','2024-09-14 21:14:40'),
(5,5,'2024-09-14 21:14:40','2024-09-14 21:14:40'),
(5,13,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(5,14,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(6,6,'2024-09-14 21:14:40','2024-09-14 21:14:40'),
(7,7,'2024-09-14 21:14:40','2024-09-14 21:14:40'),
(8,8,'2024-09-14 21:14:40','2024-09-14 21:14:40'),
(8,15,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(8,16,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(9,9,'2024-09-14 21:14:40','2024-09-14 21:14:40'),
(10,10,'2024-09-14 21:14:40','2024-09-14 21:14:40'),
(11,11,'2024-09-14 21:14:40','2024-09-14 21:14:40'),
(12,12,'2024-09-14 21:14:40','2024-09-14 21:14:40'),
(13,13,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(13,15,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(14,14,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(14,15,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(16,13,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(16,14,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(16,17,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(17,15,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(17,16,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(18,14,'2024-09-14 21:14:41','2024-09-14 21:14:41');
/*!40000 ALTER TABLE `entities_and_tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `entity`
--

DROP TABLE IF EXISTS `entity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `entity` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `created_by_id` int(11) DEFAULT NULL,
  `updated_by_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_entity_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `entity`
--

LOCK TABLES `entity` WRITE;
/*!40000 ALTER TABLE `entity` DISABLE KEYS */;
INSERT INTO `entity` VALUES
(1,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(2,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(3,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(4,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(5,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(6,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(7,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(8,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(9,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(10,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(11,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(12,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(13,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(14,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(15,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(16,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(17,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(18,'2024-09-14 21:14:41','2024-09-14 21:14:41',NULL,NULL);
/*!40000 ALTER TABLE `entity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `folder`
--

DROP TABLE IF EXISTS `folder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `folder` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `entity_id` int(11) NOT NULL,
  `tenant_id` int(11) NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `created_by_id` int(11) DEFAULT NULL,
  `updated_by_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `entity_id` (`entity_id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `parent_id` (`parent_id`),
  KEY `ix_folder_id` (`id`),
  KEY `ix_folder_name` (`name`),
  CONSTRAINT `folder_ibfk_1` FOREIGN KEY (`entity_id`) REFERENCES `entity` (`id`),
  CONSTRAINT `folder_ibfk_2` FOREIGN KEY (`tenant_id`) REFERENCES `tenant` (`id`),
  CONSTRAINT `folder_ibfk_3` FOREIGN KEY (`parent_id`) REFERENCES `folder` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `folder`
--

LOCK TABLES `folder` WRITE;
/*!40000 ALTER TABLE `folder` DISABLE KEYS */;
INSERT INTO `folder` VALUES
(1,'/',2,1,NULL,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(2,'/',4,2,NULL,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(3,'folder1',5,1,1,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(4,'sub11',6,1,3,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(5,'sub12',7,1,3,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(6,'folder2',8,1,1,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(7,'sub21',9,1,6,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(8,'sub22',10,1,6,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(9,'folder3',11,2,2,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(10,'sub31',12,2,9,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL);
/*!40000 ALTER TABLE `folder` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `created_by_id` int(11) DEFAULT NULL,
  `updated_by_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_role_name` (`name`),
  KEY `ix_role_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` VALUES
(1,'admin','2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(2,'owner','2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(3,'user','2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL);
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tag`
--

DROP TABLE IF EXISTS `tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `tenant_id` int(11) DEFAULT NULL,
  `type` enum('DEVICE','FOLDER','TENANT','USER','GLOBAL','USER_CREATED') NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `created_by_id` int(11) DEFAULT NULL,
  `updated_by_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `ix_tag_name` (`name`),
  KEY `ix_tag_id` (`id`),
  CONSTRAINT `tag_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenant` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tag`
--

LOCK TABLES `tag` WRITE;
/*!40000 ALTER TABLE `tag` DISABLE KEYS */;
INSERT INTO `tag` VALUES
(1,'tenant-tenant1-tag',1,'TENANT','2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(2,'folder-root-tenant-1-tag',1,'FOLDER','2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(3,'tenant-tenant2-tag',2,'TENANT','2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(4,'folder-root-tenant-2-tag',2,'FOLDER','2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(5,'folder-tenant1-folder1-tag',1,'FOLDER','2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(6,'folder-tenant1-sub11-tag',1,'FOLDER','2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(7,'folder-tenant1-sub12-tag',1,'FOLDER','2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(8,'folder-tenant1-folder2-tag',1,'FOLDER','2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(9,'folder-tenant1-sub21-tag',1,'FOLDER','2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(10,'folder-tenant1-sub22-tag',1,'FOLDER','2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(11,'folder-tenant2-folder3-tag',2,'FOLDER','2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(12,'folder-tenant2-sub31-tag',2,'FOLDER','2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(13,'tag-1',1,'USER_CREATED','2024-09-14 21:14:41','2024-09-14 21:14:41',NULL,NULL),
(14,'tag-2',1,'USER_CREATED','2024-09-14 21:14:41','2024-09-14 21:14:41',NULL,NULL),
(15,'tag-3',2,'USER_CREATED','2024-09-14 21:14:41','2024-09-14 21:14:41',NULL,NULL),
(16,'tag-4',2,'USER_CREATED','2024-09-14 21:14:41','2024-09-14 21:14:41',NULL,NULL),
(17,'tag-global-1',NULL,'GLOBAL','2024-09-14 21:14:41','2024-09-14 21:14:41',NULL,NULL);
/*!40000 ALTER TABLE `tag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenant`
--

DROP TABLE IF EXISTS `tenant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenant` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `entity_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `created_by_id` int(11) DEFAULT NULL,
  `updated_by_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `entity_id` (`entity_id`),
  KEY `ix_tenant_name` (`name`),
  KEY `ix_tenant_id` (`id`),
  CONSTRAINT `tenant_ibfk_1` FOREIGN KEY (`entity_id`) REFERENCES `entity` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenant`
--

LOCK TABLES `tenant` WRITE;
/*!40000 ALTER TABLE `tenant` DISABLE KEYS */;
INSERT INTO `tenant` VALUES
(1,'tenant1',1,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(2,'tenant2',3,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL);
/*!40000 ALTER TABLE `tenant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenants_and_users`
--

DROP TABLE IF EXISTS `tenants_and_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tenants_and_users` (
  `tenant_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`tenant_id`,`user_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `tenants_and_users_ibfk_1` FOREIGN KEY (`tenant_id`) REFERENCES `tenant` (`id`) ON DELETE CASCADE,
  CONSTRAINT `tenants_and_users_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenants_and_users`
--

LOCK TABLES `tenants_and_users` WRITE;
/*!40000 ALTER TABLE `tenants_and_users` DISABLE KEYS */;
INSERT INTO `tenants_and_users` VALUES
(1,1,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(1,3,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(2,1,'2024-09-14 21:14:41','2024-09-14 21:14:41'),
(2,2,'2024-09-14 21:14:41','2024-09-14 21:14:41');
/*!40000 ALTER TABLE `tenants_and_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `disabled` tinyint(1) NOT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `last_login` datetime NOT NULL,
  `entity_id` int(11) NOT NULL,
  `role_id` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `created_by_id` int(11) DEFAULT NULL,
  `updated_by_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_user_username` (`username`),
  KEY `entity_id` (`entity_id`),
  KEY `role_id` (`role_id`),
  KEY `ix_user_id` (`id`),
  CONSTRAINT `user_ibfk_1` FOREIGN KEY (`entity_id`) REFERENCES `entity` (`id`),
  CONSTRAINT `user_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES
(1,'test-user-1@sia.com',0,'$2b$12$j1lgnf0843cEiEDS1483We2pd/WaxJUoT8D/XuzMSSNhPXqVoZpfC','2024-09-14 21:14:40',16,1,'2024-09-14 21:14:40','2024-09-14 21:14:40',NULL,NULL),
(2,'test-user-2@sia.com',0,'$2b$12$kZpyNGAC/ulot6yB4l5EJuedAymSUfB9NTUECDCZBSLJIm8KMywCW','2024-09-14 21:14:41',17,2,'2024-09-14 21:14:41','2024-09-14 21:14:41',NULL,NULL),
(3,'test-user-3@sia.com',0,'$2b$12$.oDupDOjWXYu3rfiaTOPO.dwQNuBAF4krcckqfKozoOut2sj7WDze','2024-09-14 21:14:41',18,3,'2024-09-14 21:14:41','2024-09-14 21:14:41',NULL,NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2024-09-15 19:21:49
