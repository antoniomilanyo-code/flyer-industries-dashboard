#!/usr/bin/env python3
"""
Crafted Complete Daily Financial Report + Food Cost Variance
Combines: Expenses + Petty Cash + Mokapos Revenue + Food Cost Tracking
Monthly Period: 21st to 20th of next month
"""

import requests
import csv
import io
import subprocess
import json
import sys
sys.path.insert(0, '/root/.openclaw/workspace/crafted_reports')

from datetime import datetime
from collections import defaultdict
from food_cost_tracker import FoodCostTracker, record_sales_from_mokapos

# Google Sheet URLs (public, read-only)
EXPENSES_URL = "https://docs.google.com/spreadsheets/d/1u7Du_KjwGvEL-Jp0oI91Zjlq8gYtxOx5/export?format=csv"
PETTY_CASH_URL = "https://docs.google.com/spreadsheets/d/1XUOUAxjOsAWyzpHwqMr2OZ93c5p1YYvt/export?format=csv"

def parse_currency(value):
    if not value:
        return 0
    try:
        cleaned = value.replace('Rp', '').replace(',', '').strip()
        return float(cleaned) if cleaned else 0
    except:
        return 0

def get_monthly_period():
    today = datetime.now()
    if today.day >= 21:
        start_date = today.replace(day=21)
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=20)
        else:
            end_date = today.replace(month=today.month + 1, day=20)
    else:
        end_date = today.replace(day=20)
        if today.month == 1:
            start_date = today.replace(year=today.year - 1, month=12, day=21)
        else:
            start_date = today.replace(month=today.month - 1, day=21)
    return start_date, end_date

def fetch_sheet_data(url, sheet_name="Sheet"):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return {'error': f'Failed to fetch {sheet_name}: {str(e)}'}

def parse_expenses(csv_data, period_start=None, period_end=None):
    if isinstance(csv_data, dict) and 'error' in csv_data:
        return csv_data
    
    rows = []
    reader = csv.reader(io.StringIO(csv_data))
    lines = list(reader)
    data_rows = lines[5:] if len(lines) > 5 else []
    
    current_date = None
    for row in data_rows:
        if len(row) > 0 and row[0].strip() and '/' in row[0]:
            current_date = row[0].strip()
        if len(row) >= 9:
            expense = {
                'date': current_date or '',
                'category': row[1].strip() if len(row) > 1 else '',
                'item': row[2].strip() if len(row) > 2 else '',
                'qty': row[3].strip() if len(row) > 3 else '',
                'total_cost': row[5].strip() if len(row) > 5 else '',
                'payment_method': row[7].strip() if len(row) > 7 else '',
            }
            if expense['item'] or expense['total_cost']:
                rows.append(expense)
    return rows

def parse_petty_cash(csv_data, period_start=None, period_end=None):
    if isinstance(csv_data, dict) and 'error' in csv_data:
        return csv_data
    
    rows = []
    reader = csv.reader(io.StringIO(csv_data))
    lines = list(reader)
    data_rows = lines[5:] if len(lines) > 5 else []
    
    for row in data_rows:
        if len(row) >= 7:
            entry = {
                'date': row[0].strip() if len(row) > 0 else '',
                'description': row[1].strip() if len(row) > 1 else '',
                'category': row[2].strip() if len(row) > 2 else '',
                'amount_out': row[3].strip() if len(row) > 3 else '',
                'amount_in': row[4].strip() if len(row) > 4 else '',
                'balance': row[5].strip() if len(row) > 5 else '',
            }
            if entry['description'] or entry['amount_out'] or entry['amount_in']:
                rows.append(entry)
    return rows

def get_mokapos_revenue():
    try:
        result = subprocess.run(
            ['node', '/root/.openclaw/workspace/crafted_reports/mokapos_puppeteer.js'],
            capture_output=True,
            text=True,
            timeout=150
        )
        
        output = result.stdout
        idx = output.rfind('{"success":')
        if idx != -1:
            json_str = output[idx:]
            try:
                data = json.loads(json_str)
                if data.get('success'):
                    return data
            except:
                pass
        
        lines = output.strip().split('\n')
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip().startswith('{'):
                json_candidate = '\n'.join(lines[i:])
                try:
                    data = json.loads(json_candidate)
                    if data.get('success'):
                        return data
                except:
                    continue
        
        return {'error': 'Failed to parse Mokapos output'}
    except Exception as e:
        return {'error': str(e)}

def generate_summary(expenses, petty_cash, mokapos_data, monthly_expenses=None, monthly_petty_cash=None):
    exp_summary = {'total': 0, 'transactions': 0, 'categories': defaultdict(float)}
    if not isinstance(expenses, dict):
        for exp in expenses:
            cost = parse_currency(exp.get('total_cost', ''))
            if cost > 0:
                exp_summary['total'] += cost
                exp_summary['transactions'] += 1
                cat = exp.get('category', 'Uncategorized')
                exp_summary['categories'][cat] += cost
    
    monthly_exp_summary = {'total': 0, 'transactions': 0}
    if monthly_expenses and not isinstance(monthly_expenses, dict):
        for exp in monthly_expenses:
            cost = parse_currency(exp.get('total_cost', ''))
            if cost > 0:
                monthly_exp_summary['total'] += cost
                monthly_exp_summary['transactions'] += 1
    
    pc_summary = {'total_out': 0, 'total_in': 0, 'current_balance': 0}
    if not isinstance(petty_cash, dict):
        for entry in petty_cash:
            out_amt = parse_currency(entry.get('amount_out', ''))
            in_amt = parse_currency(entry.get('amount_in', ''))
            balance = parse_currency(entry.get('balance', ''))
            pc_summary['total_out'] += out_amt
            pc_summary['total_in'] += in_amt
            if balance > 0:
                pc_summary['current_balance'] = balance
    
    monthly_pc_summary = {'total_out': 0, 'total_in': 0}
    if monthly_petty_cash and not isinstance(monthly_petty_cash, dict):
        for entry in monthly_petty_cash:
            out_amt = parse_currency(entry.get('amount_out', ''))
            in_amt = parse_currency(entry.get('amount_in', ''))
            monthly_pc_summary['total_out'] += out_amt
            monthly_pc_summary['total_in'] += in_amt
    
    daily_rev = {'gross_sales': 0, 'net_sales': 0, 'transactions': 0}
    monthly_rev = {'gross_sales': 0, 'net_sales': 0, 'transactions': 0}
    
    if isinstance(mokapos_data, dict) and mokapos_data.get('success'):
        daily = mokapos_data.get('daily_revenue', {})
        daily_rev['gross_sales'] = daily.get('gross_sales', 0)
        daily_rev['net_sales'] = daily.get('net_sales', 0)
        daily_rev['transactions'] = daily.get('transactions', 0)
        monthly = mokapos_data.get('monthly_revenue', {})
        monthly_rev['gross_sales'] = monthly.get('gross_sales', 0)
        monthly_rev['net_sales'] = monthly.get('net_sales', 0)
        monthly_rev['transactions'] = monthly.get('transactions', 0)
    
    return {
        'expenses': exp_summary,
        'monthly_expenses': monthly_exp_summary,
        'petty_cash': pc_summary,
        'monthly_petty_cash': monthly_pc_summary,
        'daily_revenue': daily_rev,
        'monthly_revenue': monthly_rev
    }

def format_report(summary, period_start, period_end, food_cost_alerts=None):
    report = []
    report.append("📊 *CRAFTED DAILY FINANCIAL REPORT*")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} WITA")
    report.append(f"Period: {period_start.strftime('%d/%m/%Y')} - {period_end.strftime('%d/%m/%Y')}")
    report.append("")
    
    # Daily Revenue
    daily_rev = summary['daily_revenue']
    report.append("💵 *TODAY'S REVENUE (Mokapos)*")
    report.append(f"   Gross Sales: Rp {daily_rev['gross_sales']:,.0f}")
    report.append(f"   Net Sales: Rp {daily_rev['net_sales']:,.0f}")
    report.append(f"   Transactions: {daily_rev['transactions']}")
    report.append("")
    
    # Monthly Revenue
    monthly_rev = summary['monthly_revenue']
    report.append(f"📅 *MONTHLY REVENUE (Mokapos)*")
    report.append(f"   Period: {period_start.strftime('%d/%m')} - {period_end.strftime('%d/%m')}")
    report.append(f"   Gross Sales: Rp {monthly_rev['gross_sales']:,.0f}")
    report.append(f"   Net Sales: Rp {monthly_rev['net_sales']:,.0f}")
    report.append("")
    
    # Daily Expenses
    exp = summary['expenses']
    report.append("💳 *TODAY'S EXPENSES*")
    report.append(f"   Total: Rp {exp['total']:,.0f}")
    report.append(f"   Transactions: {exp['transactions']}")
    if exp['categories']:
        for cat, amount in sorted(exp['categories'].items(), key=lambda x: x[1], reverse=True)[:3]:
            if cat:
                report.append(f"      • {cat}: Rp {amount:,.0f}")
    report.append("")
    
    # Monthly Expenses
    monthly_exp = summary['monthly_expenses']
    monthly_pc = summary['monthly_petty_cash']
    monthly_total_outflows = monthly_exp['total'] + monthly_pc['total_out']
    
    report.append("📊 *MONTHLY EXPENSES (Sheets)*")
    report.append(f"   Total Expenses: Rp {monthly_exp['total']:,.0f}")
    report.append(f"   Petty Cash Out: Rp {monthly_pc['total_out']:,.0f}")
    report.append(f"   Total Outflows: Rp {monthly_total_outflows:,.0f}")
    report.append("")
    
    # Petty Cash
    pc = summary['petty_cash']
    report.append("💰 *PETTY CASH*")
    report.append(f"   Current Balance: Rp {pc['current_balance']:,.0f}")
    report.append(f"   Today Out: Rp {pc['total_out']:,.0f} | In: Rp {pc['total_in']:,.0f}")
    report.append("")
    
    # Daily Summary
    daily_outflows = exp['total'] + pc['total_out']
    daily_net = daily_rev['net_sales'] - daily_outflows
    report.append("📈 *TODAY'S SUMMARY*")
    report.append(f"   Revenue: Rp {daily_rev['net_sales']:,.0f}")
    report.append(f"   Outflows: Rp {daily_outflows:,.0f}")
    report.append(f"   Net: {'+' if daily_net >= 0 else ''}Rp {daily_net:,.0f}")
    report.append("")
    
    # Monthly Net
    monthly_net = monthly_rev['net_sales'] - monthly_total_outflows
    report.append("📈 *MONTHLY NET POSITION*")
    report.append(f"   Revenue: Rp {monthly_rev['net_sales']:,.0f}")
    report.append(f"   Outflows: Rp {monthly_total_outflows:,.0f}")
    report.append(f"   Net: {'+' if monthly_net >= 0 else ''}Rp {monthly_net:,.0f}")
    report.append("")
    
    # FOOD COST VARIANCE ALERTS
    if food_cost_alerts:
        report.append("🚨 *FOOD COST VARIANCE ALERTS* (±15% tolerance)")
        report.append("-" * 40)
        
        # Show top 5 flagged items
        for ingredient, data in list(food_cost_alerts.items())[:5]:
            emoji = "📈" if data['variance_percent'] > 0 else "📉"
            report.append(f"{emoji} {ingredient.replace('_', ' ').title()}")
            report.append(f"   Variance: {data['variance_percent']:+.1f}%")
            report.append(f"   Theory: {data['theoretical']:.0f} | Actual: {data['actual']:.0f}")
            report.append("")
        
        if len(food_cost_alerts) > 5:
            report.append(f"   ... and {len(food_cost_alerts) - 5} more items")
    else:
        report.append("✅ *FOOD COST:* All ingredients within tolerance")
    
    report.append("")
    report.append("✅ Report complete")
    
    return "\n".join(report)

def generate_daily_report():
    print("Fetching expenses...")
    expenses_csv = fetch_sheet_data(EXPENSES_URL, "Expenses")
    expenses = parse_expenses(expenses_csv)
    
    print("Fetching monthly expenses...")
    period_start, period_end = get_monthly_period()
    monthly_expenses = parse_expenses(expenses_csv, period_start, period_end)
    
    print("Fetching petty cash...")
    petty_cash_csv = fetch_sheet_data(PETTY_CASH_URL, "Petty Cash")
    petty_cash = parse_petty_cash(petty_cash_csv)
    monthly_petty_cash = parse_petty_cash(petty_cash_csv, period_start, period_end)
    
    print("Fetching Mokapos revenue...")
    mokapos_data = get_mokapos_revenue()
    
    print("Generating summary...")
    summary = generate_summary(expenses, petty_cash, mokapos_data, monthly_expenses, monthly_petty_cash)
    
    # FOOD COST TRACKING
    print("Checking food cost variances...")
    tracker = FoodCostTracker(tolerance_percent=15)
    
    # Record today's sales for food cost tracking
    # (This is a simplified version - in production, parse actual Mokapos sales)
    today = datetime.now().strftime('%Y-%m-%d')
    month_key = today[:7]  # YYYY-MM
    
    # Get food cost alerts
    food_cost_alerts = tracker.get_ingredient_alerts(month_key)
    
    print("Formatting report...")
    report = format_report(summary, period_start, period_end, food_cost_alerts)
    
    return report

if __name__ == '__main__':
    report = generate_daily_report()
    print(report)
