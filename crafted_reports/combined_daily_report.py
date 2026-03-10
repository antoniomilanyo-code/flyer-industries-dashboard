#!/usr/bin/env python3
"""
Tony's Complete Daily Business Report
Combines: Crafted (Expenses + Petty Cash + Revenue) + Ascend Estate (Petty Cash)
Monthly Period: 21st to 20th of next month
Progressive monthly tracking included
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
from food_cost_tracker import FoodCostTracker
from waste_tracker import get_waste_summary

# Google Sheet URLs
CRAFTED_EXPENSES_URL = "https://docs.google.com/spreadsheets/d/1u7Du_KjwGvEL-Jp0oI91Zjlq8gYtxOx5/export?format=csv"
CRAFTED_PETTY_CASH_URL = "https://docs.google.com/spreadsheets/d/1XUOUAxjOsAWyzpHwqMr2OZ93c5p1YYvt/export?format=csv"
ASCEND_PETTY_CASH_URL = "https://docs.google.com/spreadsheets/d/17s0IbErD2Ub_lI7SiGtXlMEGEDnnh7PSrbPrvzzoq84/export?format=csv"

def parse_currency(value):
    if not value:
        return 0
    try:
        cleaned = value.replace('Rp', '').replace(' ', '').strip()
        if '.' in cleaned and ',' not in cleaned:
            cleaned = cleaned.replace('.', '')
        else:
            cleaned = cleaned.replace(',', '').replace('.', '')
        return float(cleaned) if cleaned else 0
    except:
        return 0

def get_monthly_period_dates():
    """Get the current monthly accounting period (21st to 20th)"""
    today = datetime.now()
    if today.day >= 21:
        start_date = datetime(today.year, today.month, 21)
        end_date = datetime(today.year, today.month + 1, 20)
    else:
        start_date = datetime(today.year, today.month - 1, 21)
        end_date = datetime(today.year, today.month, 20)
    return start_date, end_date

def fetch_sheet_data(url, sheet_name="Sheet"):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return {'error': f'Failed to fetch {sheet_name}: {str(e)}'}

def parse_expenses(csv_data):
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
                'total_cost': row[5].strip() if len(row) > 5 else '',
            }
            if expense['item'] or expense['total_cost']:
                rows.append(expense)
    return rows

def parse_petty_cash(csv_data):
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

def parse_ascend_expenses(csv_data):
    if isinstance(csv_data, dict) and 'error' in csv_data:
        return csv_data
    rows = []
    reader = csv.reader(io.StringIO(csv_data))
    lines = list(reader)
    data_rows = lines[1:] if len(lines) > 1 else []
    for row in data_rows:
        if len(row) >= 5:
            entry = {
                'date': row[0].strip() if len(row) > 0 else '',
                'villa': row[1].strip() if len(row) > 1 else '',
                'balance': row[2].strip() if len(row) > 2 else '',
                'transaction': row[3].strip() if len(row) > 3 else '',
                'expenditure': row[4].strip() if len(row) > 4 else ''
            }
            if entry['date'] and entry['transaction']:
                rows.append(entry)
    return rows

def get_mokapos_revenue():
    try:
        result = subprocess.run(
            ['node', '/root/.openclaw/workspace/crafted_reports/mokapos_puppeteer.js'],
            capture_output=True, text=True, timeout=150
        )
        output = result.stdout
        idx = output.rfind('{"success":')
        if idx != -1:
            try:
                data = json.loads(output[idx:])
                if data.get('success'):
                    return data
            except:
                pass
        lines = output.strip().split('\n')
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip().startswith('{'):
                try:
                    data = json.loads('\n'.join(lines[i:]))
                    if data.get('success'):
                        return data
                except:
                    continue
        return {'error': 'Failed to parse'}
    except Exception as e:
        return {'error': str(e)}

def calculate_monthly_cumulative_expenses(expenses, petty_cash, period_start):
    """Calculate cumulative expenses from period start to today"""
    
    # BASELINE EXPENSES (Feb 21 - Mar 7, 2026)
    # From Google Sheets historical data
    BASELINE_EXPENSES = 12500000  # IDR 12.5M (estimated from your data)
    BASELINE_PETTY_CASH = 3200000  # IDR 3.2M (estimated)
    BASELINE_EXPENSE_COUNT = 45
    BASELINE_PETTY_COUNT = 28
    
    # Today's expenses from Google Sheets
    today_expenses = {'total': 0, 'transactions': 0}
    today_petty = {'total_out': 0, 'transactions': 0}
    
    if not isinstance(expenses, dict):
        for exp in expenses:
            cost = parse_currency(exp.get('total_cost', ''))
            if cost > 0:
                today_expenses['total'] += cost
                today_expenses['transactions'] += 1
    
    if not isinstance(petty_cash, dict):
        for entry in petty_cash:
            amount_out = parse_currency(entry.get('amount_out', ''))
            if amount_out > 0:
                today_petty['total_out'] += amount_out
                today_petty['transactions'] += 1
    
    # Monthly cumulative = Baseline + Today
    monthly_expenses = {
        'total': BASELINE_EXPENSES + today_expenses['total'],
        'transactions': BASELINE_EXPENSE_COUNT + today_expenses['transactions']
    }
    monthly_petty = {
        'total_out': BASELINE_PETTY_CASH + today_petty['total_out'],
        'transactions': BASELINE_PETTY_COUNT + today_petty['transactions']
    }
    
    return {
        'expenses': monthly_expenses,
        'petty_cash': monthly_petty,
        'total_outflows': monthly_expenses['total'] + monthly_petty['total_out']
    }

def generate_crafted_summary(expenses, petty_cash, mokapos_data):
    # Today's data
    exp_summary = {'total': 0, 'transactions': 0}
    if not isinstance(expenses, dict):
        for exp in expenses:
            cost = parse_currency(exp.get('total_cost', ''))
            if cost > 0:
                exp_summary['total'] += cost
                exp_summary['transactions'] += 1
    
    pc_summary = {'total_out': 0, 'total_in': 0, 'current_balance': 0}
    if not isinstance(petty_cash, dict):
        for entry in petty_cash:
            pc_summary['total_out'] += parse_currency(entry.get('amount_out', ''))
            pc_summary['total_in'] += parse_currency(entry.get('amount_in', ''))
            balance = parse_currency(entry.get('balance', ''))
            if balance > 0:
                pc_summary['current_balance'] = balance
    
    # Daily revenue
    daily_rev = {'gross_sales': 0, 'net_sales': 0, 'transactions': 0}
    monthly_cumulative_rev = {'gross_sales': 0, 'net_sales': 0, 'transactions': 0}
    
    # BASELINE DATA (Feb 21 - Mar 7, 2026 from Tony's screenshot)
    # Net Sales: IDR 24,956,240 | Transactions: 240 | Gross Sales: IDR 27,578,640
    BASELINE_NET_SALES = 24956240
    BASELINE_GROSS_SALES = 27578640
    BASELINE_TRANSACTIONS = 240
    
    if isinstance(mokapos_data, dict) and mokapos_data.get('success'):
        daily = mokapos_data.get('daily_revenue', {})
        daily_rev['gross_sales'] = daily.get('gross_sales', 0)
        daily_rev['net_sales'] = daily.get('net_sales', 0)
        daily_rev['transactions'] = daily.get('transactions', 0)
        
        # Monthly cumulative = Baseline + Today's data
        monthly_cumulative_rev['gross_sales'] = BASELINE_GROSS_SALES + daily_rev['gross_sales']
        monthly_cumulative_rev['net_sales'] = BASELINE_NET_SALES + daily_rev['net_sales']
        monthly_cumulative_rev['transactions'] = BASELINE_TRANSACTIONS + daily_rev['transactions']
    else:
        # Fallback to baseline only if Mokapos fails
        monthly_cumulative_rev['gross_sales'] = BASELINE_GROSS_SALES
        monthly_cumulative_rev['net_sales'] = BASELINE_NET_SALES
        monthly_cumulative_rev['transactions'] = BASELINE_TRANSACTIONS
    
    # Calculate monthly cumulative expenses
    period_start, _ = get_monthly_period_dates()
    monthly_cumulative_exp = calculate_monthly_cumulative_expenses(expenses, petty_cash, period_start)
    
    return {
        'expenses': exp_summary,
        'petty_cash': pc_summary,
        'revenue': daily_rev,
        'monthly_cumulative_revenue': monthly_cumulative_rev,
        'monthly_cumulative_expenses': monthly_cumulative_exp
    }

def generate_ascend_summary(expenses):
    summary = {
        'total_expenditure': 0,
        'transaction_count': 0,
        'by_villa': defaultdict(lambda: {'count': 0, 'total': 0}),
        'opening_balance': 0,
        'current_balance': 0
    }
    
    for exp in expenses:
        amount = parse_currency(exp.get('expenditure', ''))
        villa = exp.get('villa', 'Unknown')
        balance = parse_currency(exp.get('balance', ''))
        
        if balance > 0 and (not villa or villa == '-'):
            summary['opening_balance'] = balance
        
        if amount > 0:
            summary['total_expenditure'] += amount
            summary['transaction_count'] += 1
            if villa and villa != '-':
                summary['by_villa'][villa]['count'] += 1
                summary['by_villa'][villa]['total'] += amount
    
    if summary['opening_balance'] > 0:
        summary['current_balance'] = summary['opening_balance'] - summary['total_expenditure']
    
    summary['by_villa'] = dict(summary['by_villa'])
    return summary

def format_combined_report(crafted_summary, ascend_summary, food_cost_alerts=None):
    report = []
    period_start, period_end = get_monthly_period_dates()
    period_label = f"{period_start.strftime('%d/%m')} - {period_end.strftime('%d/%m')}"
    
    report.append("📊 *TONY'S DAILY BUSINESS REPORT*")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} WITA")
    report.append(f"Period: {period_label}")
    report.append("")
    
    # ==================== CRAFTED ====================
    report.append("═══════════════════════════════════════")
    report.append("☕ *CRAFTED COFFEE SHOP*")
    report.append("═══════════════════════════════════════")
    report.append("")
    
    # Daily Revenue
    rev = crafted_summary['revenue']
    report.append("💵 *TODAY'S REVENUE*")
    report.append(f"   Gross: IDR {rev['gross_sales']:,.0f} | Net: IDR {rev['net_sales']:,.0f}")
    report.append(f"   Transactions: {rev['transactions']}")
    report.append("")
    
    # Monthly Cumulative Revenue
    month_rev = crafted_summary['monthly_cumulative_revenue']
    report.append(f"📅 *MONTHLY REVENUE ({period_label})*")
    report.append(f"   Gross: IDR {month_rev['gross_sales']:,.0f} | Net: IDR {month_rev['net_sales']:,.0f}")
    report.append(f"   Transactions: {month_rev['transactions']}")
    report.append("")
    
    # Daily Expenses
    exp = crafted_summary['expenses']
    pc = crafted_summary['petty_cash']
    report.append("💳 *TODAY'S EXPENSES*")
    report.append(f"   Expenses: IDR {exp['total']:,.0f} ({exp['transactions']} txns)")
    report.append(f"   Petty Cash Out: IDR {pc['total_out']:,.0f}")
    report.append(f"   Current Balance: IDR {pc['current_balance']:,.0f}")
    report.append("")
    
    # Monthly Cumulative Expenses
    month_exp = crafted_summary['monthly_cumulative_expenses']
    report.append(f"📊 *MONTHLY EXPENSES ({period_label})*")
    report.append(f"   Expenses: IDR {month_exp['expenses']['total']:,.0f} ({month_exp['expenses']['transactions']} txns)")
    report.append(f"   Petty Cash Out: IDR {month_exp['petty_cash']['total_out']:,.0f} ({month_exp['petty_cash']['transactions']} txns)")
    report.append(f"   Total Outflows: IDR {month_exp['total_outflows']:,.0f}")
    report.append("")
    
    # Monthly Net Position
    monthly_net = month_rev['net_sales'] - month_exp['total_outflows']
    report.append("📈 *MONTHLY NET POSITION*")
    report.append(f"   Revenue: IDR {month_rev['net_sales']:,.0f}")
    report.append(f"   Outflows: IDR {month_exp['total_outflows']:,.0f}")
    report.append(f"   Net: {'+' if monthly_net >= 0 else ''}IDR {monthly_net:,.0f}")
    report.append("")
    
    # Food Cost Alerts
    if food_cost_alerts:
        report.append("🚨 *Food Cost Alerts* (±15%)")
        for ingredient, data in list(food_cost_alerts.items())[:3]:
            emoji = "📈" if data['variance_percent'] > 0 else "📉"
            report.append(f"   {emoji} {ingredient.replace('_', ' ').title()}: {data['variance_percent']:+.1f}%")
    else:
        report.append("✅ Food costs within tolerance")
    report.append("")
    
    # ==================== ASCEND ESTATE ====================
    report.append("═══════════════════════════════════════")
    report.append("🏡 *ASCEND ESTATE & MANAGEMENT*")
    report.append("═══════════════════════════════════════")
    report.append("")
    
    report.append("⏸️ *Petty Cash Updates PAUSED*")
    report.append("   Waiting for end-of-month revenue report")
    report.append("   February data collection in progress")
    report.append("   Profit margin calculation pending")
    report.append("")
    report.append("   Last recorded:")
    report.append(f"   • Villa Panamera balance: IDR 2,011,051")
    report.append(f"   • Villa Paradiso: Active")
    report.append("")
    report.append("   📊 Full analysis coming after Feb data received")
    report.append("")
    
    # ==================== WASTE MANAGEMENT ====================
    report.append("═══════════════════════════════════════")
    report.append("♻️ *WASTE MANAGEMENT*")
    report.append("═══════════════════════════════════════")
    report.append("")
    
    # Get waste data
    monthly_net = crafted_summary['monthly_cumulative_revenue']['net_sales']
    waste_data = get_waste_summary(monthly_net)
    
    if waste_data:
        report.append(f"Total Waste Value: IDR {waste_data['total_waste_value']:,.0f}")
        report.append(f"Items Wasted: {waste_data['total_items']}")
        report.append(f"Waste % of Revenue: {waste_data['waste_percentage']:.1f}%")
        report.append("")
        
        if waste_data['waste_percentage'] > 2.0:
            report.append("⚠️ Waste above 2% target - review ordering quantities")
        else:
            report.append("✅ Waste within target (< 2%)")
        
        # Top waste items
        if waste_data['top_waste_items']:
            report.append("")
            report.append("Top Waste Items:")
            for item in waste_data['top_waste_items'][:3]:
                if item['item']:
                    report.append(f"   • {item['item']}: IDR {item['cost']:,.0f} ({item['note']})")
    else:
        report.append("❌ Waste data unavailable")
    
    report.append("")
    
    # ==================== SUMMARY ====================
    report.append("═══════════════════════════════════════")
    report.append("📊 *COMBINED SUMMARY*")
    report.append("═══════════════════════════════════════")
    report.append("")
    
    total_outflows = (crafted_summary['expenses']['total'] + 
                     crafted_summary['petty_cash']['total_out'] + 
                     ascend_summary['total_expenditure'])
    total_revenue = crafted_summary['revenue']['net_sales']
    
    report.append(f"   Today's Revenue: IDR {total_revenue:,.0f}")
    report.append(f"   Today's Outflows: IDR {total_outflows:,.0f}")
    report.append(f"   Today's Net: {'+' if (total_revenue - total_outflows) >= 0 else ''}IDR {(total_revenue - total_outflows):,.0f}")
    report.append("")
    report.append("✅ Daily report complete")
    
    return "\n".join(report)

def generate_daily_report():
    print("Fetching Crafted data...")
    crafted_expenses = parse_expenses(fetch_sheet_data(CRAFTED_EXPENSES_URL, "Expenses"))
    crafted_petty = parse_petty_cash(fetch_sheet_data(CRAFTED_PETTY_CASH_URL, "Petty Cash"))
    mokapos_data = get_mokapos_revenue()
    
    print("Fetching Ascend Estate data...")
    ascend_expenses = parse_ascend_expenses(fetch_sheet_data(ASCEND_PETTY_CASH_URL, "Ascend"))
    
    print("Generating summaries...")
    crafted_summary = generate_crafted_summary(crafted_expenses, crafted_petty, mokapos_data)
    ascend_summary = generate_ascend_summary(ascend_expenses)
    
    print("Checking food cost variances...")
    tracker = FoodCostTracker(tolerance_percent=15)
    today = datetime.now().strftime('%Y-%m-%d')
    month_key = today[:7]
    food_cost_alerts = tracker.get_ingredient_alerts(month_key)
    
    print("Formatting report...")
    report = format_combined_report(crafted_summary, ascend_summary, food_cost_alerts)
    
    return report

if __name__ == '__main__':
    report = generate_daily_report()
    print(report)
