#!/usr/bin/env python3
"""
Daily Data Push to Supabase
Runs after 11 PM cron to store financial data
"""

import requests
import json
import subprocess
import sys
sys.path.insert(0, '/root/.openclaw/workspace/crafted_reports')

from datetime import datetime
from food_cost_tracker import FoodCostTracker

# Supabase Config
SUPABASE_URL = "https://kidbbtdnhtncxtaqqgcp.supabase.co"
SUPABASE_KEY = "sb_publishable_9tYmqkG3w3UWYToiuzzoSw_KNib98xb"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def supabase_insert(table, data):
    """Insert data into Supabase table"""
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/{table}",
            headers=HEADERS,
            json=data,
            timeout=30
        )
        if response.status_code in [200, 201]:
            print(f"✅ {table}: Inserted successfully")
            return True
        else:
            print(f"❌ {table}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ {table}: Error - {str(e)}")
        return False

def supabase_upsert(table, data, unique_columns):
    """Upsert data (insert or update)"""
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/{table}",
            headers={**HEADERS, "Prefer": "resolution=merge-duplicates"},
            json=data,
            timeout=30
        )
        if response.status_code in [200, 201]:
            print(f"✅ {table}: Upserted successfully")
            return True
        else:
            print(f"❌ {table}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ {table}: Error - {str(e)}")
        return False

def get_mokapos_data():
    """Get revenue from Mokapos scraper"""
    try:
        result = subprocess.run(
            ['node', '/root/.openclaw/workspace/crafted_reports/mokapos_puppeteer.js'],
            capture_output=True, text=True, timeout=150
        )
        output = result.stdout
        idx = output.rfind('{"success":')
        if idx != -1:
            return json.loads(output[idx:])
    except:
        pass
    return None

def get_monthly_period():
    """Get current monthly period (21st-20th)"""
    today = datetime.now()
    if today.day >= 21:
        start = datetime(today.year, today.month, 21)
        end = datetime(today.year, today.month + 1, 20)
    else:
        start = datetime(today.year, today.month - 1, 21)
        end = datetime(today.year, today.month, 20)
    return start, end

def push_daily_data():
    """Main function to push daily data to Supabase"""
    print("=" * 50)
    print("📊 Daily Data Push to Supabase")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')} WITA")
    print("=" * 50)
    
    # Get today's data
    mokapos = get_mokapos_data()
    today = datetime.now().strftime('%Y-%m-%d')
    month_key = today[:7]
    
    if not mokapos:
        print("❌ Failed to get Mokapos data")
        return False
    
    daily_revenue = mokapos.get('daily_revenue', {})
    gross = daily_revenue.get('gross_sales', 0)
    net = daily_revenue.get('net_sales', 0)
    transactions = daily_revenue.get('transactions', 0)
    
    print(f"\n📈 Today's Revenue:")
    print(f"   Gross: IDR {gross:,.0f}")
    print(f"   Net: IDR {net:,.0f}")
    print(f"   Transactions: {transactions}")
    
    # 1. Push daily_revenue
    revenue_data = {
        "business_id": 1,  # Crafted
        "date": today,
        "gross_sales": gross,
        "net_sales": net,
        "transactions": transactions,
        "source": "mokapos"
    }
    supabase_upsert("daily_revenue", revenue_data, ["business_id", "date"])
    
    # 2. Push expenses (placeholder - will be fetched from Google Sheets in future)
    # For now, using static data
    
    # 3. Update/Create monthly summary
    period_start, period_end = get_monthly_period()
    
    # Get current monthly total by querying daily_revenue
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/daily_revenue?business_id=eq.1&date=gte.{period_start.strftime('%Y-%m-%d')}&select=net_sales",
            headers=HEADERS,
            timeout=30
        )
        if response.status_code == 200:
            daily_records = response.json()
            monthly_total = sum(float(r.get('net_sales', 0)) for r in daily_records)
        else:
            monthly_total = net  # Fallback to today's net
    except:
        monthly_total = net
    
    print(f"\n📅 Monthly Period: {period_start.strftime('%d/%m')} - {period_end.strftime('%d/%m')}")
    print(f"   Monthly Revenue (cumulative): IDR {monthly_total:,.0f}")
    
    # Push monthly summary
    summary_data = {
        "business_id": 1,
        "month_key": month_key,
        "start_date": period_start.strftime('%Y-%m-%d'),
        "end_date": period_end.strftime('%Y-%m-%d'),
        "total_revenue": monthly_total,
        "total_expenses": 0,  # Will be calculated from expenses table
        "total_petty_cash_out": 0,  # Will be calculated
        "net_position": monthly_total
    }
    supabase_upsert("monthly_summaries", summary_data, ["business_id", "month_key"])
    
    # 4. Push food cost alerts if any
    tracker = FoodCostTracker(tolerance_percent=15)
    alerts = tracker.get_ingredient_alerts(month_key)
    
    if alerts:
        print(f"\n🚨 Food Cost Alerts: {len(alerts)} items")
        for ingredient, data in alerts.items():
            alert_data = {
                "ingredient": ingredient,
                "theoretical_usage": data['theoretical'],
                "actual_usage": data['actual'],
                "variance_percent": data['variance_percent'],
                "tolerance_percent": 15,
                "status": "pending",
                "month_key": month_key
            }
            supabase_upsert("food_cost_alerts", alert_data, ["ingredient", "month_key"])
    else:
        print("\n✅ Food costs within tolerance")
    
    print("\n" + "=" * 50)
    print("✅ Daily data push complete!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    push_daily_data()
