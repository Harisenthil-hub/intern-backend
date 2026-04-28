-- Migration: make inventory_transactions generic and add gas_issues table

CREATE TABLE IF NOT EXISTS gas_issues (
  id INT AUTO_INCREMENT PRIMARY KEY,
  issue_code VARCHAR(20) NOT NULL UNIQUE,
  tank_id VARCHAR(20) NOT NULL,
  gas_type VARCHAR(50) NOT NULL,
  date DATE NOT NULL,
  quantity_issued DOUBLE NOT NULL,
  filling_batch_id VARCHAR(80) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'draft',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX (issue_code),
  INDEX (tank_id),
  CONSTRAINT fk_issue_tank FOREIGN KEY (tank_id) REFERENCES tanks(tank_id) ON DELETE RESTRICT
);

SET @inventory_reference_fk = (
  SELECT CONSTRAINT_NAME
  FROM information_schema.KEY_COLUMN_USAGE
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'inventory_transactions'
    AND COLUMN_NAME = 'reference_id'
    AND REFERENCED_TABLE_NAME IS NOT NULL
  LIMIT 1
);

SET @drop_inventory_fk_sql = IF(
  @inventory_reference_fk IS NOT NULL,
  CONCAT('ALTER TABLE inventory_transactions DROP FOREIGN KEY ', @inventory_reference_fk),
  'SELECT 1'
);

PREPARE drop_inventory_fk_stmt FROM @drop_inventory_fk_sql;
EXECUTE drop_inventory_fk_stmt;
DEALLOCATE PREPARE drop_inventory_fk_stmt;

ALTER TABLE inventory_transactions
  MODIFY COLUMN type VARCHAR(10) NOT NULL,
  MODIFY COLUMN reference_type VARCHAR(50) NOT NULL;
