-- Supabase Database Setup for Telegram Expense Bot
-- Run this script in your Supabase SQL Editor to set up the required tables

-- Users table: stores whitelisted Telegram users
CREATE TABLE IF NOT EXISTS users (
  "id" SERIAL PRIMARY KEY,
  "telegram_id" text UNIQUE NOT NULL,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP
);

-- Expenses table: stores user expenses
CREATE TABLE IF NOT EXISTS expenses (
  "id" SERIAL PRIMARY KEY,
  "user_id" integer NOT NULL REFERENCES users("id") ON DELETE CASCADE,
  "description" text NOT NULL,
  "amount" money NOT NULL,
  "category" text NOT NULL CHECK (category IN (
    'Housing', 'Transportation', 'Food', 'Utilities', 
    'Insurance', 'Medical/Healthcare', 'Savings', 
    'Debt', 'Education', 'Entertainment', 'Other'
  )),
  "added_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users("telegram_id");
CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses("user_id");
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses("category");
CREATE INDEX IF NOT EXISTS idx_expenses_added_at ON expenses("added_at");

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Views for analytics
CREATE OR REPLACE VIEW expense_summary_by_category AS
SELECT 
  category,
  COUNT(*) as transaction_count,
  SUM(amount::numeric) as total_amount,
  AVG(amount::numeric) as average_amount
FROM expenses 
GROUP BY category
ORDER BY total_amount DESC;

CREATE OR REPLACE VIEW user_expense_summary AS
SELECT 
  u.telegram_id,
  COUNT(e.id) as total_transactions,
  SUM(e.amount::numeric) as total_spent,
  MIN(e.added_at) as first_expense,
  MAX(e.added_at) as last_expense
FROM users u
LEFT JOIN expenses e ON u.id = e.user_id
GROUP BY u.id, u.telegram_id
ORDER BY total_spent DESC;

-- Enable Row Level Security (RLS) for Supabase
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users (you can modify these based on your security requirements)
-- Policy for users table - users can only access their own data
CREATE POLICY "Users can view own data" ON users
  FOR ALL USING (auth.uid()::text = telegram_id);

-- Policy for expenses table - users can only access their own expenses
CREATE POLICY "Users can view own expenses" ON expenses
  FOR ALL USING (
    user_id IN (
      SELECT id FROM users WHERE telegram_id = auth.uid()::text
    )
  );

-- Grant necessary permissions to the service role (for your bot)
-- Note: You might need to adjust these based on your Supabase setup
GRANT ALL ON users TO service_role;
GRANT ALL ON expenses TO service_role;
GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO service_role;
GRANT USAGE, SELECT ON SEQUENCE expenses_id_seq TO service_role; 