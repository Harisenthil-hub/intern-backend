-- Migration: create loss_records table for loss / leakage monitoring

CREATE TABLE IF NOT EXISTS loss_records (
  id INT AUTO_INCREMENT PRIMARY KEY,
  record_code VARCHAR(20) NOT NULL UNIQUE,
  tank_id VARCHAR(20) NOT NULL,
  date DATE NOT NULL,
  expected_quantity DOUBLE NOT NULL,
  actual_quantity DOUBLE NOT NULL,
  loss_quantity DOUBLE NOT NULL DEFAULT 0,
  reason VARCHAR(50) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'draft',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX (record_code),
  INDEX (tank_id),
  CONSTRAINT fk_loss_record_tank FOREIGN KEY (tank_id) REFERENCES tanks(tank_id) ON DELETE RESTRICT
);
