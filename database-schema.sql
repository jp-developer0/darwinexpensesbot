-- Database schema for Telegram Expense Bot

-- Create database (uncomment if needed)
-- CREATE DATABASE expense_bot;

-- Users table: stores whitelisted Telegram users
CREATE TABLE users (
  "id" SERIAL PRIMARY KEY,
  "telegram_id" text UNIQUE NOT NULL,
  "created_at" timestamp DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp DEFAULT CURRENT_TIMESTAMP
);

-- Expenses table: stores user expenses
CREATE TABLE expenses (
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
CREATE INDEX idx_users_telegram_id ON users("telegram_id");
CREATE INDEX idx_expenses_user_id ON expenses("user_id");
CREATE INDEX idx_expenses_category ON expenses("category");
CREATE INDEX idx_expenses_added_at ON expenses("added_at");

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Sample data (uncomment to add test data)
/*
-- Add a test user (replace with your actual Telegram ID)
INSERT INTO users (telegram_id) VALUES ('123456789');

-- Add sample expenses
INSERT INTO expenses (user_id, description, amount, category, added_at) VALUES
  (1, 'Grocery shopping', 75.50, 'Food', '2024-01-01 10:00:00'),
  (1, 'Gas station', 45.00, 'Transportation', '2024-01-01 15:30:00'),
  (1, 'Internet bill', 59.99, 'Utilities', '2024-01-02 09:15:00'),
  (1, 'Pizza delivery', 23.50, 'Food', '2024-01-02 19:45:00'),
  (1, 'Movie tickets', 28.00, 'Entertainment', '2024-01-03 20:00:00');
*/

-- Views for analytics (optional)
CREATE VIEW expense_summary_by_category AS
SELECT 
  category,
  COUNT(*) as transaction_count,
  SUM(amount::numeric) as total_amount,
  AVG(amount::numeric) as average_amount
FROM expenses 
GROUP BY category
ORDER BY total_amount DESC;

CREATE VIEW user_expense_summary AS
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