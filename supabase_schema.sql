-- Flyer Industries Database Schema
-- Run this in Supabase SQL Editor

-- Businesses table
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

-- Daily Revenue table
CREATE TABLE IF NOT EXISTS daily_revenue (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id),
    date DATE NOT NULL,
    gross_sales NUMERIC(12,2) DEFAULT 0,
    net_sales NUMERIC(12,2) DEFAULT 0,
    transactions INTEGER DEFAULT 0,
    source TEXT DEFAULT 'mokapos',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(business_id, date)
);

-- Expenses table
CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id),
    date DATE NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    amount NUMERIC(12,2) NOT NULL,
    type TEXT DEFAULT 'expense', -- expense, petty_cash_out, petty_cash_in
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Properties table (for Ascend Estate)
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

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    business_id INTEGER REFERENCES businesses(id),
    type TEXT NOT NULL,
    status TEXT DEFAULT 'planning', -- planning, in_progress, completed
    description TEXT,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recipes table
CREATE TABLE IF NOT EXISTS recipes (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL, -- beverage, food
    category TEXT,
    ingredients JSONB DEFAULT '[]',
    cost_price NUMERIC(8,2),
    sell_price NUMERIC(8,2),
    profit_margin NUMERIC(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Food Cost Alerts table
CREATE TABLE IF NOT EXISTS food_cost_alerts (
    id SERIAL PRIMARY KEY,
    ingredient TEXT NOT NULL,
    theoretical_usage NUMERIC(8,2),
    actual_usage NUMERIC(8,2),
    variance_percent NUMERIC(5,2),
    tolerance_percent NUMERIC(5,2) DEFAULT 15,
    status TEXT DEFAULT 'pending', -- pending, acknowledged, resolved
    month_key TEXT NOT NULL, -- YYYY-MM format
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(ingredient, month_key)
);

-- Monthly Summaries table
CREATE TABLE IF NOT EXISTS monthly_summaries (
    id SERIAL PRIMARY KEY,
    business_id INTEGER REFERENCES businesses(id),
    month_key TEXT NOT NULL, -- YYYY-MM
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

-- Insert initial businesses
INSERT INTO businesses (name, type, location, description, priority) VALUES
('Crafted', 'coffee_shop', 'Berawa, Bali', 'Coffee shop in Berawa', 'high'),
('Ascend Estate', 'real_estate', 'Bali', 'Villa management company', 'high'),
('TaxMate', 'tax_service', 'Australia', 'Tax services for Australian clients', 'high')
ON CONFLICT DO NOTHING;

-- Insert initial properties
INSERT INTO properties (name, type, location, status, opening_balance, current_balance) VALUES
('Villa Panamera', 'villa', 'Canggu', 'active', 2121051, 2033051),
('Golden Hour Villas', 'villa', 'Dalung', 'active', 0, 0),
('Black Sand Resort', 'resort', 'Amed', 'active', 0, 0)
ON CONFLICT DO NOTHING;

-- Insert initial projects
INSERT INTO projects (name, business_id, type, status, description) VALUES
('Villa Nativa', 2, 'construction', 'in_progress', 'New villa construction'),
('Taycana Apartments', 2, 'construction', 'in_progress', 'Apartment complex development')
ON CONFLICT DO NOTHING;

-- Enable Row Level Security (RLS)
ALTER TABLE businesses ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_revenue ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipes ENABLE ROW LEVEL SECURITY;
ALTER TABLE food_cost_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE monthly_summaries ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access (adjust as needed)
CREATE POLICY "Allow public read" ON businesses FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON daily_revenue FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON expenses FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON properties FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON projects FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON recipes FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON food_cost_alerts FOR SELECT USING (true);
CREATE POLICY "Allow public read" ON monthly_summaries FOR SELECT USING (true);

-- Allow public insert/update (for dashboard updates)
CREATE POLICY "Allow public insert" ON businesses FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update" ON businesses FOR UPDATE USING (true);
CREATE POLICY "Allow public insert" ON daily_revenue FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update" ON daily_revenue FOR UPDATE USING (true);
CREATE POLICY "Allow public insert" ON expenses FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update" ON expenses FOR UPDATE USING (true);
CREATE POLICY "Allow public insert" ON monthly_summaries FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update" ON monthly_summaries FOR UPDATE USING (true);
