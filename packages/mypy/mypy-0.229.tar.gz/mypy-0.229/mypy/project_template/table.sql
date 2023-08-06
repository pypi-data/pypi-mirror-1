-- MySQL dump 10.11
--
-- Host: localhost    Database: zuroc_wtree
-- ------------------------------------------------------
-- Server version	5.0.54-log
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `user` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `name` char(8) collate utf8_bin NOT NULL,
  `url` varchar(32) collate utf8_bin default NULL,
  `ver` tinyint(3) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `url` (`url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `user_apply`
--

DROP TABLE IF EXISTS `user_apply`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `user_apply` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `ck` binary(6) NOT NULL,
  `time` timestamp NOT NULL default CURRENT_TIMESTAMP,
  `name` varchar(8) collate utf8_bin default NULL,
  PRIMARY KEY  (`id`),
  KEY `time` (`time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `user_email`
--

DROP TABLE IF EXISTS `user_email`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `user_email` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `email` varchar(128) collate utf8_bin default NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM AUTO_INCREMENT=10000000 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `user_password`
--

DROP TABLE IF EXISTS `user_password`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `user_password` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `password` binary(32) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `user_profile`
--

DROP TABLE IF EXISTS `user_profile`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `user_profile` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `sex` char(1) character set ascii collate ascii_bin default NULL,
  `birth_age` tinyint(3) unsigned default NULL,
  `is_single` tinyint(4) default NULL,
  `industry` tinyint(3) unsigned default NULL,
  `title` varchar(16) collate utf8_bin default NULL,
  `city` smallint(5) unsigned default NULL,
  `hometown` smallint(5) unsigned default NULL,
  PRIMARY KEY  (`id`),
  KEY `industry` (`industry`),
  KEY `city_hometown` (`city`,`hometown`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `user_reset_password`
--

DROP TABLE IF EXISTS `user_reset_password`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `user_reset_password` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `ck` binary(6) NOT NULL,
  `time` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`id`),
  KEY `time` (`time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `user_session`
--

DROP TABLE IF EXISTS `user_session`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `user_session` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `session` binary(6) NOT NULL,
  `time` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`id`),
  KEY `time` (`time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
SET character_set_client = @saved_cs_client;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2009-09-23  5:06:25
