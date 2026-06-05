BEGIN;

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sales' AND column_name = 'bill_number')
     AND NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sales' AND column_name = 'invoice_number')
  THEN
    ALTER TABLE sales RENAME COLUMN bill_number TO invoice_number;
  END IF;
END $$;

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sales' AND column_name = 'cashier_name')
     AND NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sales' AND column_name = 'cashier_id')
  THEN
    ALTER TABLE sales ADD COLUMN cashier_id INTEGER;
    UPDATE sales s SET cashier_id = u.id FROM users u WHERE u.username = s.cashier_name;
    UPDATE sales SET cashier_id = COALESCE((SELECT id FROM users WHERE username = 'admin' LIMIT 1), 1) WHERE cashier_id IS NULL;
    ALTER TABLE sales ALTER COLUMN cashier_id SET NOT NULL;
    ALTER TABLE sales ADD CONSTRAINT sales_cashier_id_fkey FOREIGN KEY (cashier_id) REFERENCES users(id);
    ALTER TABLE sales DROP COLUMN cashier_name;
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sales' AND column_name = 'discount')
  THEN
    ALTER TABLE sales ADD COLUMN discount NUMERIC(10,2) NOT NULL DEFAULT 0;
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sales' AND column_name = 'net_amount')
  THEN
    ALTER TABLE sales ADD COLUMN net_amount NUMERIC(10,2);
    UPDATE sales SET net_amount = total_amount WHERE net_amount IS NULL;
    ALTER TABLE sales ALTER COLUMN net_amount SET NOT NULL;
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sales' AND column_name = 'is_voided')
  THEN
    ALTER TABLE sales ADD COLUMN is_voided BOOLEAN NOT NULL DEFAULT FALSE;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sales' AND column_name = 'status')
    THEN
      UPDATE sales SET is_voided = TRUE WHERE LOWER(status) IN ('voided','cancelled','canceled');
    END IF;
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_sales_invoice_number ON sales(invoice_number);
CREATE INDEX IF NOT EXISTS ix_sales_is_voided ON sales(is_voided);
CREATE INDEX IF NOT EXISTS ix_sales_created_at ON sales(created_at);

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'sales_invoice_number_key')
  THEN
    ALTER TABLE sales ADD CONSTRAINT sales_invoice_number_key UNIQUE (invoice_number);
  END IF;
END $$;

COMMIT;
