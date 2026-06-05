-- ============================================================================
-- Migration: Align Supabase schema with SQLAlchemy models
-- Generated: 2026
-- Purpose: Fix schema drift between local POS model and cloud backend
-- WARNING: Review each statement. Run in a transaction. Backup first.
-- ============================================================================

-- Start transaction
BEGIN;

-- 1. Rename bill_number -> invoice_number (the field the model expects)
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'sales' AND column_name = 'bill_number'
  ) AND NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'sales' AND column_name = 'invoice_number'
  ) THEN
    ALTER TABLE sales RENAME COLUMN bill_number TO invoice_number;
  END IF;
END $$;

-- 2. Rename cashier_name -> cashier_id (and convert to integer FK)
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'sales' AND column_name = 'cashier_name'
  ) AND NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'sales' AND column_name = 'cashier_id'
  ) THEN
    -- Step A: Add the new column as nullable integer
    ALTER TABLE sales ADD COLUMN cashier_id INTEGER;

    -- Step B: Try to map cashier_name (text) to cashier_id (integer)
    --         by matching against users.username
    UPDATE sales s
    SET cashier_id = u.id
    FROM users u
    WHERE u.username = s.cashier_name;

    -- Step C: For unmapped rows, assign to admin (id=1) as fallback
    UPDATE sales
    SET cashier_id = COALESCE(
      (SELECT id FROM users WHERE username = 'admin' LIMIT 1),
      1
    )
    WHERE cashier_id IS NULL;

    -- Step D: Now enforce NOT NULL and add FK
    ALTER TABLE sales ALTER COLUMN cashier_id SET NOT NULL;
    ALTER TABLE sales ADD CONSTRAINT sales_cashier_id_fkey
      FOREIGN KEY (cashier_id) REFERENCES users(id);

    -- Step E: Drop the old text column
    ALTER TABLE sales DROP COLUMN cashier_name;
  END IF;
END $$;

-- 3. Add discount column (default 0)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'sales' AND column_name = 'discount'
  ) THEN
    ALTER TABLE sales ADD COLUMN discount NUMERIC(10, 2) NOT NULL DEFAULT 0;
  END IF;
END $$;

-- 4. Add net_amount column (default to total_amount for existing rows)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'sales' AND column_name = 'net_amount'
  ) THEN
    ALTER TABLE sales ADD COLUMN net_amount NUMERIC(10, 2);
    UPDATE sales SET net_amount = total_amount WHERE net_amount IS NULL;
    ALTER TABLE sales ALTER COLUMN net_amount SET NOT NULL;
  END IF;
END $$;

-- 5. Add is_voided column
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'sales' AND column_name = 'is_voided'
  ) THEN
    -- If status column exists, use it to backfill is_voided
    ALTER TABLE sales ADD COLUMN is_voided BOOLEAN NOT NULL DEFAULT FALSE;
    IF EXISTS (
      SELECT 1 FROM information_schema.columns
      WHERE table_name = 'sales' AND column_name = 'status'
    ) THEN
      UPDATE sales SET is_voided = TRUE WHERE LOWER(status) IN ('voided', 'cancelled', 'canceled');
      UPDATE sales SET is_voided = FALSE WHERE LOWER(status) IN ('completed', 'paid', 'complete');
    END IF;
  END IF;
END $$;

-- 6. Add index on invoice_number (model expects it indexed)
CREATE INDEX IF NOT EXISTS ix_sales_invoice_number ON sales(invoice_number);

-- 7. Add index on is_voided (model expects it indexed)
CREATE INDEX IF NOT EXISTS ix_sales_is_voided ON sales(is_voided);

-- 8. Add index on created_at (model expects it indexed)
CREATE INDEX IF NOT EXISTS ix_sales_created_at ON sales(created_at);

-- 9. Ensure unique constraint on invoice_number
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'sales_invoice_number_key'
  ) THEN
    ALTER TABLE sales ADD CONSTRAINT sales_invoice_number_key UNIQUE (invoice_number);
  END IF;
END $$;

-- Commit transaction
COMMIT;

-- ============================================================================
-- Verification queries (run these manually after migration to confirm)
-- ============================================================================
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'sales'
-- ORDER BY ordinal_position;
