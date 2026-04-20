-- MySQL dump 10.13  Distrib 8.0.45, for Linux (x86_64)
--
-- Host: localhost    Database: server_inventory
-- ------------------------------------------------------
-- Server version	8.0.45-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `gpu_inventory`
--

DROP TABLE IF EXISTS `gpu_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gpu_inventory` (
  `id` int NOT NULL AUTO_INCREMENT,
  `server_name` varchar(150) NOT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `manufacturer` varchar(100) DEFAULT NULL,
  `model` varchar(150) DEFAULT NULL,
  `serial_number` varchar(100) DEFAULT NULL,
  `vram_gb` int DEFAULT NULL,
  `gpu_uuid` varchar(50) DEFAULT NULL,
  `cuda_vers` int DEFAULT NULL,
  `no_of_gpu` varchar(100) DEFAULT NULL,
  `driver_version` varchar(50) DEFAULT NULL,
  `firmware_version` varchar(50) DEFAULT NULL,
  `environment` enum('production','staging','development','testing') DEFAULT 'production',
  `status` enum('active','inactive','faulty','maintenance','decommissioned') DEFAULT 'active',
  `purchase_date` date DEFAULT NULL,
  `owners` varchar(150) DEFAULT NULL,
  `notes` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gpu_inventory`
--

LOCK TABLES `gpu_inventory` WRITE;
/*!40000 ALTER TABLE `gpu_inventory` DISABLE KEYS */;
INSERT INTO `gpu_inventory` VALUES (1,'physocgpu01prmv','192.168.52.10','NVIDIA','A100 80GB SXM4','SN-GPU-A100-001',80,'SXM4',6912,'1','535.104.12','None','production','active','2023-01-15','ml-team','None','2026-04-17 21:32:20','2026-04-17 23:58:33'),(2,'gpu-ml-002',NULL,'NVIDIA','A100 80GB SXM4','SN-GPU-A100-002',80,'SXM4',6912,'ML training','535.104.12',NULL,'production','active','2023-01-15','ml-team',NULL,'2026-04-17 21:32:20','2026-04-17 21:32:20'),(4,'gpu-dev-001',NULL,'AMD','Radeon RX 7900 XTX','SN-GPU-AMD-001',24,'PCIe 4.0 x16',12288,'rendering','23.9.1',NULL,'development','active','2023-03-20','dev-team',NULL,'2026-04-17 21:32:20','2026-04-17 21:32:20'),(5,'phyaicgpu01prmv','10.10.1.10','NVIDIA','H100','100023456A',40,'GPU01',1208,'1','535.104.12','None','production','active','2026-04-17','LAB-SOC','None','2026-04-17 23:58:00','2026-04-17 23:58:00');
/*!40000 ALTER TABLE `gpu_inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `license_inventory`
--

DROP TABLE IF EXISTS `license_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `license_inventory` (
  `id` int NOT NULL AUTO_INCREMENT,
  `software_name` varchar(150) NOT NULL,
  `vendor` varchar(100) DEFAULT NULL,
  `license_type` varchar(100) DEFAULT NULL,
  `license_key` varchar(255) DEFAULT NULL,
  `quantity` int DEFAULT '1',
  `used_count` int DEFAULT '0',
  `assigned_to` varchar(200) DEFAULT NULL,
  `purchase_date` date DEFAULT NULL,
  `expiry_date` date DEFAULT NULL,
  `cost` decimal(10,2) DEFAULT NULL,
  `support_contact` varchar(150) DEFAULT NULL,
  `notes` text,
  `status` enum('active','expired','pending_renewal','cancelled') DEFAULT 'active',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `license_inventory`
--

LOCK TABLES `license_inventory` WRITE;
/*!40000 ALTER TABLE `license_inventory` DISABLE KEYS */;
INSERT INTO `license_inventory` VALUES (1,'VMware vSphere Enterprise Plus','VMware','per-cpu subscription','XXXXX-XXXXX-XXXXX',10,8,NULL,'2023-01-01','2024-12-31',45000.00,NULL,NULL,'active','2026-04-07 04:00:14','2026-04-07 04:00:14'),(2,'Red Hat Enterprise Linux','Red Hat','per-server subscription','RH-XXXXX',25,20,'None','2023-03-01','2024-02-28',12500.00,'None','None','active','2026-04-07 04:00:14','2026-04-12 02:21:06'),(3,'Microsoft Windows Server 2022','Microsoft','per-core perpetual','MSFT-XXXXX',16,12,'None','2022-06-15','2026-04-06',8000.00,'None','None','active','2026-04-07 04:00:14','2026-04-12 02:20:49');
/*!40000 ALTER TABLE `license_inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `physical_inventory`
--

DROP TABLE IF EXISTS `physical_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `physical_inventory` (
  `id` int NOT NULL AUTO_INCREMENT,
  `hostname` varchar(100) NOT NULL,
  `asset_tag` varchar(50) DEFAULT NULL,
  `server_type` varchar(50) DEFAULT NULL,
  `manufacturer` varchar(100) DEFAULT NULL,
  `model` varchar(100) DEFAULT NULL,
  `serial_number` varchar(100) DEFAULT NULL,
  `cpu` varchar(100) DEFAULT NULL,
  `cpu_cores` int DEFAULT NULL,
  `ram_gb` int DEFAULT NULL,
  `storage` varchar(200) DEFAULT NULL,
  `datacenter` varchar(100) DEFAULT NULL,
  `rack_location` varchar(50) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `os` varchar(100) DEFAULT NULL,
  `status` enum('active','inactive','decommissioned','maintenance') DEFAULT 'active',
  `purchase_date` date DEFAULT NULL,
  `notes` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `asset_tag` (`asset_tag`),
  UNIQUE KEY `serial_number` (`serial_number`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `physical_inventory`
--

LOCK TABLES `physical_inventory` WRITE;
/*!40000 ALTER TABLE `physical_inventory` DISABLE KEYS */;
INSERT INTO `physical_inventory` VALUES (1,'srv-prod-001','ASSET-001','rack','Dell','PowerEdge R740','SN-DELL-001','Intel Xeon Gold 6248R',64,256,'4x 1.8TB SAS RAID10','DC-East','R12-U040','10.10.1.10','RHEL 9.0','active','2022-03-15','None','2026-04-07 04:00:14','2026-04-12 02:24:15'),(2,'srv-prod-002','ASSET-002','rack','HPE','ProLiant DL380 Gen10','SN-HPE-002','Intel Xeon Silver 4210',20,128,'2x 960GB SSD RAID1','DC-East','R12-U06','10.10.1.11','Ubuntu 22.04','active','2022-06-01',NULL,'2026-04-07 04:00:14','2026-04-07 04:00:14'),(3,'srv-dev-001','ASSET-003','tower','Lenovo','ThinkSystem ST550','SN-LEN-003','Intel Xeon E-2288G',8,64,'2x 2TB SATA','DC-West','R01-U10','10.10.2.10','CentOS 7','maintenance','2021-09-10',NULL,'2026-04-07 04:00:14','2026-04-07 04:00:14');
/*!40000 ALTER TABLE `physical_inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `storage_inventory`
--

DROP TABLE IF EXISTS `storage_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `storage_inventory` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cluster_name` varchar(150) NOT NULL,
  `cluster_ipaddrs` varchar(45) DEFAULT NULL,
  `node_name` varchar(100) DEFAULT NULL,
  `node_ipaddrs` varchar(50) DEFAULT NULL,
  `mgmt_ipaddrs` varchar(50) DEFAULT NULL,
  `service_ipaddrs` varchar(50) DEFAULT NULL,
  `interclus_ipaddrs` varchar(50) DEFAULT NULL,
  `storage_type` enum('SSD','HDD','NVMe','SAN','NAS','Tape','Object','Cloud') DEFAULT 'SSD',
  `manufacturer` varchar(100) DEFAULT NULL,
  `model` varchar(150) DEFAULT NULL,
  `serial_number` varchar(100) DEFAULT NULL,
  `capacity_tb` decimal(10,2) DEFAULT NULL,
  `asset_tag` varchar(150) DEFAULT NULL,
  `used_tb` decimal(10,2) DEFAULT NULL,
  `environment` enum('production','staging','development','testing') DEFAULT 'production',
  `status` enum('active','inactive','faulty','degraded','maintenance','decommissioned') DEFAULT 'active',
  `purchase_date` date DEFAULT NULL,
  `support_end` varchar(50) DEFAULT NULL,
  `owners` varchar(150) DEFAULT NULL,
  `notes` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `storage_inventory`
--

LOCK TABLES `storage_inventory` WRITE;
/*!40000 ALTER TABLE `storage_inventory` DISABLE KEYS */;
INSERT INTO `storage_inventory` VALUES (1,'nas-prod-01','10.10.5.10','None','RAID-DP','NFS/SMB','Rack 2U','STG-001','NAS','NetApp','AFF A400','SN-NAS-001',200.00,'2009845678',120.50,'production','active','2022-08-01','2027-08-01','storage-team','None','2026-04-17 21:33:20','2026-04-20 02:49:31'),(2,'san-prod-01','10.10.5.20',NULL,'RAID-3D','FC/iSCSI','Rack 3U','STG-002','SAN','Pure Storage','FlashArray //X70','SN-SAN-001',500.00,NULL,380.00,'production','active','2022-05-15',NULL,'storage-team',NULL,'2026-04-17 21:33:20','2026-04-17 21:33:20'),(3,'nvme-srv-001',NULL,'srv-prod-001','RAID-5','NVMe PCIe 4.0','U.2 2.5\"','STG-003','NVMe','Samsung','PM9A3 7.68TB','SN-NVM-001',7.68,'/data',4.20,'production','active','2022-03-15','XFS','ops-team',NULL,'2026-04-17 21:33:20','2026-04-17 21:33:20'),(5,'Cluster01','10.20.10.100','FAS8300-01','192.168.10.10','192.168.50.100','172.150.10.100','172.10.15.10','SAN','NetApp','FAS8300','200004876',200.00,'1500004567',100.00,'production','active','2022-08-01','2022-08-01','LAB-SOC','None','2026-04-20 02:46:43','2026-04-20 02:46:43'),(6,'Cluster01','10.20.10.100','FAS8300-02','192.168.10.10','192.168.50.100','172.150.10.100','172.10.15.10','SSD','NetApp','FAS8300','2000048734',NULL,'15000045987',NULL,'production','active','2024-05-15','2028-05-15','LAB-SOC','None','2026-04-20 02:49:00','2026-04-20 02:49:00');
/*!40000 ALTER TABLE `storage_inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vendor_info`
--

DROP TABLE IF EXISTS `vendor_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vendor_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `vendor_name` varchar(150) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `contact_name` varchar(100) DEFAULT NULL,
  `contact_email` varchar(150) DEFAULT NULL,
  `contact_phone` varchar(50) DEFAULT NULL,
  `account_manager` varchar(100) DEFAULT NULL,
  `am_email` varchar(150) DEFAULT NULL,
  `am_phone` varchar(50) DEFAULT NULL,
  `website` varchar(255) DEFAULT NULL,
  `login_id` varchar(100) DEFAULT NULL,
  `address` text,
  `contract_start` date DEFAULT NULL,
  `contract_end` date DEFAULT NULL,
  `payment_terms` varchar(100) DEFAULT NULL,
  `account_number` varchar(100) DEFAULT NULL,
  `notes` text,
  `status` enum('active','inactive','blacklisted') DEFAULT 'active',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vendor_info`
--

LOCK TABLES `vendor_info` WRITE;
/*!40000 ALTER TABLE `vendor_info` DISABLE KEYS */;
INSERT INTO `vendor_info` VALUES (1,'Dell Techonologie','hardware','John Smith','support@dell.com','1-800-915-3355','Alice Johnson','alice.johnson@dell.com','None1','https://dell.com','sraitinfra@samsung.com','None','2022-01-01','2025-12-31','None','None','None','active','2026-04-07 04:00:14','2026-04-12 18:31:06'),(2,'Red Hat','software','Support Portal','support@redhat.com','1-888-733-4281','Bob Williams','bob.williams@redhat.com','None','https://redhat.com','sraitinfra@samsung.com','None','2023-01-01','2024-12-31','None','None','None','active','2026-04-07 04:00:14','2026-04-12 18:32:13'),(3,'Vmware','software','Support Portal','support@vmware.com','1-877-486-9273','Carol Davis','carol.davis@vmware.com',NULL,'https://vmware.com','sraitinfra@samsung.com',NULL,'2023-01-01','2024-12-31',NULL,NULL,NULL,'active','2026-04-07 04:00:14','2026-04-12 18:32:38'),(5,'NetApp','storage','Ramesh Selvaraj','netappsupport@netapp.com','1800458562','John asdsfd','john@netapp.com','91524635821','https://netapp.com','sraitinfra!samsung.com','None','2023-04-01','2027-04-01','None','None','Storage vendor info','active','2026-04-12 18:37:01','2026-04-12 18:53:03'),(6,'Fortinet','other',NULL,'support@fortinet.com','1-800-123456','Robrt Ailence','a.robert@fortinet.com','None','https://fortinet.com','sraitinfra@sasung.com','None','2026-04-01','2029-04-01','Annual','None','Share Point LB','active','2026-04-13 00:52:07','2026-04-13 00:52:35');
/*!40000 ALTER TABLE `vendor_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `virtual_inventory`
--

DROP TABLE IF EXISTS `virtual_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `virtual_inventory` (
  `id` int NOT NULL AUTO_INCREMENT,
  `vm_name` varchar(100) NOT NULL,
  `host_server` varchar(100) DEFAULT NULL,
  `hypervisor` varchar(50) DEFAULT NULL,
  `vcpu` int DEFAULT NULL,
  `ram_gb` int DEFAULT NULL,
  `storage_gb` int DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `os` varchar(100) DEFAULT NULL,
  `environment` enum('production','staging','development','testing') DEFAULT 'production',
  `status` enum('running','stopped','suspended','deleted') DEFAULT 'running',
  `owner` varchar(100) DEFAULT NULL,
  `project` varchar(100) DEFAULT NULL,
  `notes` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `virtual_inventory`
--

LOCK TABLES `virtual_inventory` WRITE;
/*!40000 ALTER TABLE `virtual_inventory` DISABLE KEYS */;
INSERT INTO `virtual_inventory` VALUES (1,'vm-web-prod-01','srv-prod-001','VMware ESXi 7',8,32,200,'10.10.1.100','Ubuntu 22.04','production','running','ops-team','web-frontend',NULL,'2026-04-07 04:00:14','2026-04-07 04:00:14'),(2,'vm-db-prod-01','srv-prod-001','VMware ESXi 7',16,64,500,'10.10.1.101','RHEL 8','production','running','dba-team','database',NULL,'2026-04-07 04:00:14','2026-04-07 04:00:14'),(3,'vm-dev-01','srv-dev-001','KVM',4,8,100,'10.10.2.100','Debian 11','development','running','dev-team','microservices',NULL,'2026-04-07 04:00:14','2026-04-07 04:00:14');
/*!40000 ALTER TABLE `virtual_inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `warranty_info`
--

DROP TABLE IF EXISTS `warranty_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `warranty_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `asset_tag` varchar(50) DEFAULT NULL,
  `server_name` varchar(150) NOT NULL,
  `manufacturer` varchar(100) DEFAULT NULL,
  `model` varchar(100) DEFAULT NULL,
  `serial_number` varchar(100) DEFAULT NULL,
  `service_support` varchar(100) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `support_level` varchar(50) DEFAULT NULL,
  `support_contact` varchar(150) DEFAULT NULL,
  `owners` varchar(255) DEFAULT NULL,
  `contract_number` varchar(100) DEFAULT NULL,
  `manage_by` varchar(100) DEFAULT NULL,
  `notes` text,
  `status` enum('active','expired','extended','voided') DEFAULT 'active',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warranty_info`
--

LOCK TABLES `warranty_info` WRITE;
/*!40000 ALTER TABLE `warranty_info` DISABLE KEYS */;
INSERT INTO `warranty_info` VALUES (1,'ASSET-001','srv-prod-001','Dell','PowerEdge R740','SN-DELL-001','Dell ProSupport','2022-03-15','2025-03-14','5 days a week','1-800-915-3355','SRA-LAB-MPI','None','SRA-IT-INFRA','None','active','2026-04-07 04:00:14','2026-04-12 05:25:08'),(2,'ASSET-002','srv-prod-002','HPE','ProLiant DL380 Gen10','SN-HPE-002','HPE Pointnext','2022-06-01','2025-05-31','Pro Support','1-800-633-3600','SRA-LAB-SMI','None','SRA-IT-INFRA','None','active','2026-04-07 04:00:14','2026-04-12 05:25:42'),(3,'ASSET-003','srv-dev-001','Lenovo','ThinkSystem ST550','SN-LEN-003','Lenovo Premier Support','2021-09-10','2024-09-09','9x5','1-855-253-6686','SRA-IT-INFRA','None','SRA-IT-INFRA','Labs Server','expired','2026-04-07 04:00:14','2026-04-12 05:23:11');
/*!40000 ALTER TABLE `warranty_info` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-20  3:01:52
