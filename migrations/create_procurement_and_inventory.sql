-- Migration: create gas_procurements and inventory_transactions tables

CREATE TABLE IF NOT EXISTS gas_procurements (
  id INT AUTO_INCREMENT PRIMARY KEY,
  procurement_code VARCHAR(20) NOT NULL UNIQUE,
  vendor_name VARCHAR(150) NOT NULL,
  date DATE NOT NULL,
  gas_type VARCHAR(50) NOT NULL,
  quantity_received DOUBLE NOT NULL,
  tank_id VARCHAR(20) NOT NULL,
  transport_details VARCHAR(255),
  status VARCHAR(20) NOT NULL DEFAULT 'draft',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX (procurement_code),
  INDEX (tank_id),
  CONSTRAINT fk_procurement_tank FOREIGN KEY (tank_id) REFERENCES tanks(tank_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS inventory_transactions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tank_id VARCHAR(20) NOT NULL,
  type VARCHAR(10) NOT NULL,
  reference_type VARCHAR(50) NOT NULL,
  reference_id INT NOT NULL,
  quantity DOUBLE NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX (tank_id),
  INDEX (reference_id),
  CONSTRAINT fk_inventory_procurement FOREIGN KEY (reference_id) REFERENCES gas_procurements(id) ON DELETE RESTRICT,
  CONSTRAINT fk_inventory_tank FOREIGN KEY (tank_id) REFERENCES tanks(tank_id) ON DELETE RESTRICT
);
