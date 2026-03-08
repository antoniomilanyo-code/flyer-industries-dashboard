#!/usr/bin/env python3
"""
Create Supabase Tables via SQL
This script creates all necessary tables for Flyer Industries
"""

import requests
import json

SUPABASE_URL = "https://kidbbtdnhtncxtaqqgcp.supabase.co"
SUPABASE_KEY = "sb_publishable_9tYmqkG3w3UWYToiuzzoSw_KNib98xb"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def create_table(table_name, columns):
    """Create a table via Supabase REST API"""
    # Try to create by inserting schema
    try:
        # First, try to create the table by posting to the table endpoint
        # This only works if the table already exists, but let's check
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/{table_name}?limit=0",
            headers=headers
        )
        if response.status_code == 200:
            print(f"✅ Table '{table_name}' already exists")
            return True
        elif response.status_code == 404:
            print(f"❌ Table '{table_name}' not found - needs to be created via SQL Editor")
            return False
        else:
            print(f"⚠️  Table '{table_name}': Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking table '{table_name}': {e}")
        return False

def insert_data(table_name, data):
    """Insert data into a table"""
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/{table_name}",
            headers=headers,
            json=data
        )
        if response.status_code in [200, 201]:
            print(f"✅ Data inserted into '{table_name}'")
            return True
        else:
            print(f"❌ Failed to insert into '{table_name}': {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error inserting into '{table_name}': {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 Flyer Industries - Supabase Table Setup")
    print("=" * 60)
    print()
    
    # Check existing tables
    tables = [
        "businesses",
        "daily_revenue", 
        "monthly_summaries",
        "expenses",
        "properties",
        "projects",
        "recipes",
        "food_cost_alerts"
    ]
    
    print("📋 Checking existing tables...")
    existing = []
    missing = []
    
    for table in tables:
        if create_table(table, {}):
            existing.append(table)
        else:
            missing.append(table)
    
    print()
    print(f"✅ Existing tables: {len(existing)}")
    for t in existing:
        print(f"   - {t}")
    
    print()
    print(f"❌ Missing tables: {len(missing)}")
    for t in missing:
        print(f"   - {t}")
    
    if missing:
        print()
        print("⚠️  IMPORTANT: Tables need to be created via Supabase SQL Editor")
        print()
        print("To create tables automatically, you need to:")
        print("1. Go to https://supabase.com/dashboard/project/kidbbtdnhtncxtaqqgcp")
        print("2. Click SQL Editor → New Query")
        print("3. Run the SQL from: /root/.openclaw/workspace/supabase_schema.sql")
        print()
        print("OR")
        print()
        print("Use Table Editor (Visual):")
        print("1. Go to Table Editor")
        print("2. Create each table manually with columns")
        print()
    
    # Try to insert baseline data into existing tables
    if "businesses" in existing:
        print("📝 Inserting baseline data...")
        businesses = [
            {"name": "Crafted", "type": "coffee_shop", "location": "Berawa, Bali", "description": "Coffee shop in Berawa", "priority": "high", "status": "active"},
            {"name": "Ascend Estate", "type": "real_estate", "location": "Bali", "description": "Villa management company", "priority": "high", "status": "active"},
            {"name": "TaxMate", "type": "tax_service", "location": "Australia", "description": "Tax services for Australian clients", "priority": "high", "status": "active"}
        ]
        for biz in businesses:
            insert_data("businesses", biz)
    
    if "monthly_summaries" in existing:
        print("📝 Inserting monthly summary...")
        summary = {
            "business_id": 1,
            "month_key": "2026-03",
            "start_date": "2026-02-21",
            "end_date": "2026-03-07",
            "total_revenue": 24956240,
            "total_expenses": 1250000,
            "total_petty_cash_out": 594000,
            "net_position": 23112240
        }
        insert_data("monthly_summaries", summary)
    
    if "properties" in existing:
        print("📝 Inserting properties...")
        properties = [
            {"name": "Villa Panamera", "type": "villa", "location": "Canggu", "status": "active", "opening_balance": 2121051, "current_balance": 2033051},
            {"name": "Golden Hour Villas", "type": "villa", "location": "Dalung", "status": "active"},
            {"name": "Black Sand Resort", "type": "resort", "location": "Amed", "status": "active"}
        ]
        for prop in properties:
            insert_data("properties", prop)
    
    print()
    print("=" * 60)
    print("Setup check complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
