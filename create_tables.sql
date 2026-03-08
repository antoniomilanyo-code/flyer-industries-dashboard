-- =====================================================
-- FLYER INDUSTRIES - COMPLETE DATABASE SCHEMA
-- Run this in Supabase SQL Editor
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. BUSINESSES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS businesses (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    location TEXT,
    description TEXT,
    priority TEXT DEFAULT 'normal',
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert businesses
INSERT INTO businesses (name, type, location, description, priority, status) VALUES
('Crafted', 'coffee_shop', 'Berawa, Bali', 'Coffee shop in Berawa', 'high', 'active'),
('Ascend Estate', 'real_estate', 'Bali', 'Villa management company', 'high', 'active'),
('TaxMate', 'tax_service', 'Australia', 'Tax services for Australian clients', 'high', 'active')
ON CONFLICT DO NOTHING;

-- =====================================================
-- 2. DAILY REVENUE TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS daily_revenue (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    gross_sales NUMERIC(12,2) DEFAULT 0,
    net_sales NUMERIC(12,2) DEFAULT 0,
    transactions INTEGER DEFAULT 0,
    source TEXT DEFAULT 'mokapos',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(business_id, date)
);

-- =====================================================
-- 3. EXPENSES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    type TEXT DEFAULT 'expense', -- expense, petty_cash_out, petty_cash_in
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 4. MONTHLY SUMMARIES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS monthly_summaries (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id) ON DELETE CASCADE,
    month_key TEXT NOT NULL, -- Format: YYYY-MM
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_revenue NUMERIC(12,2) DEFAULT 0,
    total_expenses NUMERIC(12,2) DEFAULT 0,
    total_petty_cash_out NUMERIC(12,2) DEFAULT 0,
    net_position NUMERIC(12,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(business_id, month_key)
);

-- Insert baseline monthly summary (Feb 21 - Mar 7, 2026)
INSERT INTO monthly_summaries (
    business_id, month_key, start_date, end_date, 
    total_revenue, total_expenses, total_petty_cash_out, net_position
) VALUES (
    1, '2026-03', '2026-02-21', '2026-03-07', 
    24956240, 1250000, 594000, 23112240
) ON CONFLICT DO NOTHING;

-- =====================================================
-- 5. PROPERTIES TABLE (Ascend Estate)
-- =====================================================
CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL, -- villa, resort, apartment
    location TEXT,
    status TEXT DEFAULT 'active',
    opening_balance NUMERIC(12,2) DEFAULT 0,
    current_balance NUMERIC(12,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert properties
INSERT INTO properties (name, type, location, status, opening_balance, current_balance) VALUES
('Villa Panamera', 'villa', 'Canggu', 'active', 2121051, 2033051),
('Golden Hour Villas', 'villa', 'Dalung', 'active', 0, 0),
('Black Sand Resort', 'resort', 'Amed', 'active', 0, 0)
ON CONFLICT DO NOTHING;

-- =====================================================
-- 6. PROJECTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    business_id INTEGER REFERENCES businesses(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    status TEXT DEFAULT 'planning', -- planning, in_progress, completed
    description TEXT,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert projects
INSERT INTO projects (name, business_id, type, status, description) VALUES
('Villa Nativa', 2, 'construction', 'in_progress', 'New villa construction'),
('Taycana Apartments', 2, 'construction', 'in_progress', 'Apartment complex development')
ON CONFLICT DO NOTHING;

-- =====================================================
-- 7. RECIPES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS recipes (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL, -- beverage, food
    category TEXT,
    ingredients JSONB DEFAULT '[]',
    cost_price NUMERIC(8,2) DEFAULT 0,
    sell_price NUMERIC(8,2) DEFAULT 0,
    profit_margin NUMERIC(5,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 8. FOOD COST ALERTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS food_cost_alerts (
    id SERIAL PRIMARY KEY,
    ingredient TEXT NOT NULL,
    theoretical_usage NUMERIC(8,2) DEFAULT 0,
    actual_usage NUMERIC(8,2) DEFAULT 0,
    variance_percent NUMERIC(5,2) DEFAULT 0,
    tolerance_percent NUMERIC(5,2) DEFAULT 15,
    status TEXT DEFAULT 'pending', -- pending, acknowledged, resolved
    month_key TEXT NOT NULL, -- Format: YYYY-MM
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(ingredient, month_key)
);

-- =====================================================
-- ENABLE ROW LEVEL SECURITY (RLS)
-- =====================================================
ALTER TABLE businesses ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_revenue ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE monthly_summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipes ENABLE ROW LEVEL SECURITY;
ALTER TABLE food_cost_alerts ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- CREATE POLICIES FOR PUBLIC ACCESS
-- =====================================================

-- Allow public read access
CREATE POLICY "Allow public read" ON businesses FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON daily_revenue FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON expenses FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON monthly_summaries FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON properties FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON projects FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON recipes FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON food_cost_alerts FOR SELECT USING (true);

-- Allow public insert/update (for dashboard updates)
CREATE POLICY "Allow public insert" ON businesses FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update" ON businesses FOR UPDATE USING (true);
CREATE POLICY "Allow public insert" ON daily_revenue FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update" ON daily_revenue FOR UPDATE USING (true);
CREATE POLICY "Allow public insert" ON expenses FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update" ON expenses FOR UPDATE USING (true);
CREATE POLICY "Allow public insert" ON monthly_summaries FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update" ON monthly_summaries FOR UPDATE USING (true);
CREATE POLICY "Allow public insert" ON properties FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update" ON properties FOR UPDATE USING (true);
CREATE POLICY "Allow public insert" ON projects FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update" ON projects FOR UPDATE USING (true);
CREATE POLICY "Allow public insert" ON recipes FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update" ON recipes FOR UPDATE USING (true);
CREATE POLICY "Allow public insert" ON food_cost_alerts FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update" ON food_cost_alerts FOR UPDATE USING (true);

-- =====================================================
-- CREATE INDEXES FOR PERFORMANCE
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_daily_revenue_date ON daily_revenue(date);
CREATE INDEX IF NOT EXISTS idx_daily_revenue_business ON daily_revenue(business_id);
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
CREATE INDEX IF NOT EXISTS idx_monthly_summaries_key ON monthly_summaries(month_key);
CREATE INDEX IF NOT EXISTS idx_food_alerts_month ON food_cost_alerts(month_key);

-- =====================================================
-- VERIFICATION
-- =====================================================
SELECT 'Tables created successfully!' as status;
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;
