/*
SQLyog Ultimate v10.42 
MySQL - 5.5.35 : Database - migrate
*********************************************************************
*/


/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`migrate` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `migrate`;

DROP TABLE IF EXISTS `PicFile`;

CREATE TABLE IF NOT EXISTS `PicFile` (
  `id` bigint(20) NOT NULL COMMENT '自增id',
  `ImgPath` varchar(64) NOT NULL DEFAULT '' COMMENT '文件名',
  `ImgExt` varchar(16) NOT NULL DEFAULT '' COMMENT '文件后缀',
  `UserId` int(10) NOT NULL DEFAULT '0' COMMENT '用户唯一ID',
  `TopId` int(10) NOT NULL DEFAULT '0' COMMENT '作品集ID',
  `md5` varchar(32) NOT NULL DEFAULT '' COMMENT 'url md5',
  `hash` varchar(64) NOT NULL DEFAULT '' COMMENT '文件hash值-七牛提供',
  `size` int(10) NOT NULL DEFAULT '0' COMMENT '文件大小-七牛提供',
  `mimeType` varchar(64) NOT NULL DEFAULT '' COMMENT '文件类型-七牛提供',
  `mtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;