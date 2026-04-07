-- Server Inventory Management System - MySQL Schema

CREATE DATABASE IF NOT EXISTS server_inventory;
USE server_inventory;

-- Physical Inventory Table
CREATE TABLE IF NOT EXISTS physical_inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hostname VARCHAR(100) NOT NULL,
    asset_tag VARCHAR(50) UNIQUE,
    server_type VARCHAR(50),          -- rack, tower, blade
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100) UNIQUE,
    cpu VARCHAR(100),
    cpu_cores INT,
    ram_gb INT,
    storage VARCHAR(200),
    datacenter VARCHAR(100),
    rack_location VARCHAR(50),
    ip_address VARCHAR(45),
    os VARCHAR(100),
    status ENUM('active','inactive','decommissioned','maintenance') DEFAULT 'active',
    purchase_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Virtual Inventory Table
CREATE TABLE IF NOT EXISTS virtual_inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vm_name VARCHAR(100) NOT NULL,
    host_server VARCHAR(100),
    hypervisor VARCHAR(50),           -- VMware, KVM, Hyper-V, etc.
    vcpu INT,
    ram_gb INT,
    storage_gb INT,
    ip_address VARCHAR(45),
    os VARCHAR(100),
    environment ENUM('production','staging','development','testing') DEFAULT 'production',
    status ENUM('running','stopped','suspended','deleted') DEFAULT 'running',
    owner VARCHAR(100),
    project VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- License Inventory Table
CREATE TABLE IF NOT EXISTS license_inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    software_name VARCHAR(150) NOT NULL,
    vendor VARCHAR(100),
    license_type VARCHAR(100),        -- perpetual, subscription, per-seat, etc.
    license_key VARCHAR(255),
    quantity INT DEFAULT 1,
    used_count INT DEFAULT 0,
    assigned_to VARCHAR(200),
    purchase_date DATE,
    expiry_date DATE,
    cost DECIMAL(10,2),
    support_contact VARCHAR(150),
    notes TEXT,
    status ENUM('active','expired','pending_renewal','cancelled') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Warranty Info Table
CREATE TABLE IF NOT EXISTS warranty_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_tag VARCHAR(50),
    device_name VARCHAR(150) NOT NULL,
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    warranty_type VARCHAR(100),       -- onsite, depot, parts-only
    provider VARCHAR(100),
    start_date DATE,
    end_date DATE,
    support_level VARCHAR(50),        -- 24x7, 9x5, NBD
    support_contact VARCHAR(150),
    ticket_url VARCHAR(255),
    contract_number VARCHAR(100),
    cost DECIMAL(10,2),
    notes TEXT,
    status ENUM('active','expired','extended','voided') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Vendor Info Table
CREATE TABLE IF NOT EXISTS vendor_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_name VARCHAR(150) NOT NULL,
    category VARCHAR(100),            -- hardware, software, cloud, support
    contact_name VARCHAR(100),
    contact_email VARCHAR(150),
    contact_phone VARCHAR(50),
    account_manager VARCHAR(100),
    am_email VARCHAR(150),
    am_phone VARCHAR(50),
    website VARCHAR(255),
    address TEXT,
    contract_start DATE,
    contract_end DATE,
    payment_terms VARCHAR(100),
    account_number VARCHAR(100),
    notes TEXT,
    status ENUM('active','inactive','blacklisted') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Sample Data

INSERT INTO physical_inventory (hostname, asset_tag, server_type, manufacturer, model, serial_number, cpu, cpu_cores, ram_gb, storage, datacenter, rack_location, ip_address, os, status, purchase_date) VALUES
('srv-prod-001', 'ASSET-001', 'rack', 'Dell', 'PowerEdge R740', 'SN-DELL-001', 'Intel Xeon Gold 6248R', 48, 256, '4x 1.8TB SAS RAID10', 'DC-East', 'R12-U04', '10.10.1.10', 'RHEL 8.6', 'active', '2022-03-15'),
('srv-prod-002', 'ASSET-002', 'rack', 'HPE', 'ProLiant DL380 Gen10', 'SN-HPE-002', 'Intel Xeon Silver 4210', 20, 128, '2x 960GB SSD RAID1', 'DC-East', 'R12-U06', '10.10.1.11', 'Ubuntu 22.04', 'active', '2022-06-01'),
('srv-dev-001', 'ASSET-003', 'tower', 'Lenovo', 'ThinkSystem ST550', 'SN-LEN-003', 'Intel Xeon E-2288G', 8, 64, '2x 2TB SATA', 'DC-West', 'R01-U10', '10.10.2.10', 'CentOS 7', 'maintenance', '2021-09-10');

INSERT INTO virtual_inventory (vm_name, host_server, hypervisor, vcpu, ram_gb, storage_gb, ip_address, os, environment, status, owner, project) VALUES
('vm-web-prod-01', 'srv-prod-001', 'VMware ESXi 7', 8, 32, 200, '10.10.1.100', 'Ubuntu 22.04', 'production', 'running', 'ops-team', 'web-frontend'),
('vm-db-prod-01', 'srv-prod-001', 'VMware ESXi 7', 16, 64, 500, '10.10.1.101', 'RHEL 8', 'production', 'running', 'dba-team', 'database'),
('vm-dev-01', 'srv-dev-001', 'KVM', 4, 8, 100, '10.10.2.100', 'Debian 11', 'development', 'running', 'dev-team', 'microservices');

INSERT INTO license_inventory (software_name, vendor, license_type, license_key, quantity, used_count, purchase_date, expiry_date, cost, status) VALUES
('VMware vSphere Enterprise Plus', 'VMware', 'per-cpu subscription', 'XXXXX-XXXXX-XXXXX', 10, 8, '2023-01-01', '2024-12-31', 45000.00, 'active'),
('Red Hat Enterprise Linux', 'Red Hat', 'per-server subscription', 'RH-XXXXX', 25, 20, '2023-03-01', '2024-02-28', 12500.00, 'active'),
('Microsoft Windows Server 2022', 'Microsoft', 'per-core perpetual', 'MSFT-XXXXX', 16, 12, '2022-06-15', NULL, 8000.00, 'active');

INSERT INTO warranty_info (asset_tag, device_name, manufacturer, model, serial_number, warranty_type, provider, start_date, end_date, support_level, support_contact, cost, status) VALUES
('ASSET-001', 'srv-prod-001', 'Dell', 'PowerEdge R740', 'SN-DELL-001', 'onsite', 'Dell ProSupport', '2022-03-15', '2025-03-14', '24x7', '1-800-915-3355', 3200.00, 'active'),
('ASSET-002', 'srv-prod-002', 'HPE', 'ProLiant DL380 Gen10', 'SN-HPE-002', 'onsite', 'HPE Pointnext', '2022-06-01', '2025-05-31', 'NBD', '1-800-633-3600', 2800.00, 'active'),
('ASSET-003', 'srv-dev-001', 'Lenovo', 'ThinkSystem ST550', 'SN-LEN-003', 'depot', 'Lenovo Premier Support', '2021-09-10', '2024-09-09', '9x5', '1-855-253-6686', 1500.00, 'expired');

INSERT INTO vendor_info (vendor_name, category, contact_name, contact_email, contact_phone, account_manager, am_email, website, contract_start, contract_end, status) VALUES
('Dell Technologies', 'hardware', 'John Smith', 'support@dell.com', '1-800-915-3355', 'Alice Johnson', 'alice.johnson@dell.com', 'https://dell.com', '2022-01-01', '2025-12-31', 'active'),
('Red Hat', 'software', 'Support Portal', 'support@redhat.com', '1-888-733-4281', 'Bob Williams', 'bob.williams@redhat.com', 'https://redhat.com', '2023-01-01', '2024-12-31', 'active'),
('VMware', 'software', 'Support Portal', 'support@vmware.com', '1-877-486-9273', 'Carol Davis', 'carol.davis@vmware.com', 'https://vmware.com', '2023-01-01', '2024-12-31', 'active');
