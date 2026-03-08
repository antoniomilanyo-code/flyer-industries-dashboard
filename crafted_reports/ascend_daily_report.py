#!/usr/bin/env python3
"""
Ascend Estate Daily Petty Cash Report
Tracks daily expenses for villa management
Villas: Panamera, Golden Hour (Paradiso & Lotus), Black Sand Resort
"""

import requests
import csv
import io
from datetime import datetime
from collections import defaultdict

# Google Sheet URL (public, read-only)
ASCEND_PETTY_CASH_URL = "https://docs.google.com/spreadsheets/d/17s0IbErD2Ub_lI7SiGtXlMEGEDnnh7PSrbPrvzzoq84/export?format=csv"

def parse_currency(value):
    """Parse currency string to float"""
    if not value:
        return 0
    try:
        cleaned = value.replace('Rp', '').replace(',', '').replace('.', '').strip()
        return float(cleaned) if cleaned else 0
    except:
        return 0

def parse_date(date_str):
    """Parse date from various formats"""
    if not date_str:
        return None
    formats = ['%d/%m/%y', '%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue
    return None

def fetch_ascend_petty_cash():
    """Fetch Ascend Estate petty cash data"""
    try:
        response = requests.get(ASCEND_PETTY_CASH_URL, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return {'error': f'Failed to fetch Ascend data: {str(e)}'}

def parse_ascend_expenses(csv_data):
    """Parse Ascend Estate CSV data"""
    if isinstance(csv_data, dict) and 'error' in csv_data:
        return csv_data
    
    rows = []
    reader = csv.reader(io.StringIO(csv_data))
    lines = list(reader)
    
    # Skip header row (row 0)
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
            # Only add if it has data
            if entry['date'] and entry['transaction']:
                rows.append(entry)
    
    return rows

def generate_summary(expenses):
    """Generate summary statistics"""
    summary = {
        'total_expenditure': 0,
        'transaction_count': 0,
        'by_villa': defaultdict(lambda: {'count': 0, 'total': 0}),
        'by_category': defaultdict(lambda: {'count': 0, 'total': 0}),
        'current_balance': 0
    }
    
    for exp in expenses:
        amount = parse_currency(exp.get('expenditure', ''))
        villa = exp.get('villa', 'Unknown')
        transaction = exp.get('transaction', '')
        
        if amount > 0:
            summary['total_expenditure'] += amount
            summary['transaction_count'] += 1
            summary['by_villa'][villa]['count'] += 1
            summary['by_villa'][villa]['total'] += amount
            
            # Try to categorize
            trans_lower = transaction.lower()
            if any(word in trans_lower for word in ['galon', 'water', 'aqua']):
                category = 'Water'
            elif any(word in trans_lower for word in ['tisue', 'tissue', 'toilet', 'soap']):
                category = 'Toiletries'
            elif any(word in trans_lower for word in ['clean', 'chemical', 'floor']):
                category = 'Cleaning'
            elif any(word in trans_lower for word in ['repair', 'fix', 'service']):
                category = 'Maintenance'
            elif any(word in trans_lower for word in ['gas', 'listrik', 'electric']):
                category = 'Utilities'
            else:
                category = 'Other'
            
            summary['by_category'][category]['count'] += 1
            summary['by_category'][category]['total'] += amount
        
        # Track latest balance
        balance = parse_currency(exp.get('balance', ''))
        if balance > 0:
            summary['current_balance'] = balance
    
    summary['by_villa'] = dict(summary['by_villa'])
    summary['by_category'] = dict(summary['by_category'])
    return summary

def format_report(summary):
    """Format the report"""
    report = []
    report.append("🏡 *ASCEND ESTATE - DAILY PETTY CASH REPORT*")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} WITA")
    report.append("")
    
    report.append("💰 *SUMMARY*")
    report.append(f"   Total Expenditure: IDR {summary['total_expenditure']:,.0f}")
    report.append(f"   Transactions: {summary['transaction_count']}")
    if summary['current_balance'] > 0:
        report.append(f"   Current Balance: IDR {summary['current_balance']:,.0f}")
    report.append("")
    
    # By Villa
    if summary['by_villa']:
        report.append("🏠 *BY VILLA*")
        for villa, data in sorted(summary['by_villa'].items(), key=lambda x: x[1]['total'], reverse=True):
            if villa and villa != '-':
                report.append(f"   • {villa}: IDR {data['total']:,.0f} ({data['count']} transactions)")
        report.append("")
    
    # By Category
    if summary['by_category']:
        report.append("📁 *BY CATEGORY*")
        for cat, data in sorted(summary['by_category'].items(), key=lambda x: x[1]['total'], reverse=True):
            report.append(f"   • {cat}: IDR {data['total']:,.0f} ({data['count']} items)")
        report.append("")
    
    report.append("✅ Ascend Estate report complete")
    return "\n".join(report)

def generate_ascend_report():
    """Main function"""
    print("Fetching Ascend Estate petty cash data...")
    csv_data = fetch_ascend_petty_cash()
    
    if isinstance(csv_data, dict) and 'error' in csv_data:
        return f"❌ Error: {csv_data['error']}"
    
    print("Parsing expenses...")
    expenses = parse_ascend_expenses(csv_data)
    
    print("Generating summary...")
    summary = generate_summary(expenses)
    
    print("Formatting report...")
    report = format_report(summary)
    
    return report

if __name__ == '__main__':
    report = generate_ascend_report()
    print(report)
