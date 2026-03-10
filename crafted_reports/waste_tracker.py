#!/usr/bin/env python3
"""
Waste Management Tracker for Crafted
Reads waste data from Google Sheet and calculates waste metrics
"""

import requests
import csv
import io
from datetime import datetime

WASTE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1aShOCX38NRjEcnjFYBzs1NRa5DX5tHym/export?format=csv"

def parse_currency_waste(value):
    """Parse Indonesian Rupiah format from waste sheet"""
    if not value:
        return 0
    try:
        # Remove Rp, spaces, and handle Indonesian number format
        cleaned = str(value).replace('Rp', '').replace(' ', '').strip()
        # Handle comma as thousand separator, dot as decimal
        cleaned = cleaned.replace('.', '').replace(',', '.')
        return float(cleaned) if cleaned else 0
    except:
        return 0

def fetch_waste_data():
    """Fetch waste data from Google Sheet"""
    try:
        response = requests.get(WASTE_SHEET_URL, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ Failed to fetch waste data: {e}")
        return None

def parse_waste_csv(csv_data):
    """Parse waste CSV data"""
    if not csv_data:
        return []
    
    rows = []
    reader = csv.reader(io.StringIO(csv_data))
    lines = list(reader)
    
    # Skip header rows (first 6 rows are headers)
    data_rows = lines[6:] if len(lines) > 6 else []
    
    for row in data_rows:
        if len(row) >= 7:
            # Check if this is the total row
            if row[0] == '' and row[6]:  # Total row has empty date but has value
                continue
                
            entry = {
                'date': row[0].strip() if len(row) > 0 else '',
                'item': row[1].strip() if len(row) > 1 else '',
                'quantity': row[2].strip() if len(row) > 2 else '',
                'note': row[3].strip() if len(row) > 3 else '',
                'employee': row[4].strip() if len(row) > 4 else '',
                'manager': row[5].strip() if len(row) > 5 else '',
                'cost': parse_currency_waste(row[6]) if len(row) > 6 else 0
            }
            if entry['item'] or entry['cost'] > 0:
                rows.append(entry)
    
    return rows

def calculate_waste_metrics(waste_data, monthly_revenue):
    """Calculate waste metrics"""
    if not waste_data:
        return None
    
    total_waste_value = sum(entry['cost'] for entry in waste_data)
    total_items = len([e for e in waste_data if e['item']])
    
    # Categorize waste
    categories = {
        'expired': [],
        'spoiled': [],
        'rotten': [],
        'stale': [],
        'other': []
    }
    
    for entry in waste_data:
        note = entry['note'].lower()
        if 'expired' in note:
            categories['expired'].append(entry)
        elif 'spoil' in note:
            categories['spoiled'].append(entry)
        elif 'rotten' in note or 'rot' in note:
            categories['rotten'].append(entry)
        elif 'stale' in note:
            categories['stale'].append(entry)
        else:
            categories['other'].append(entry)
    
    # Calculate waste % of revenue
    waste_percentage = (total_waste_value / monthly_revenue * 100) if monthly_revenue > 0 else 0
    
    # Top waste items by value
    top_waste = sorted(waste_data, key=lambda x: x['cost'], reverse=True)[:5]
    
    return {
        'total_waste_value': total_waste_value,
        'total_items': total_items,
        'waste_percentage': waste_percentage,
        'categories': {
            'expired': {'count': len(categories['expired']), 'cost': sum(e['cost'] for e in categories['expired'])},
            'spoiled': {'count': len(categories['spoiled']), 'cost': sum(e['cost'] for e in categories['spoiled'])},
            'rotten': {'count': len(categories['rotten']), 'cost': sum(e['cost'] for e in categories['rotten'])},
            'stale': {'count': len(categories['stale']), 'cost': sum(e['cost'] for e in categories['stale'])},
            'other': {'count': len(categories['other']), 'cost': sum(e['cost'] for e in categories['other'])}
        },
        'top_waste_items': top_waste
    }

def get_waste_summary(monthly_revenue=24956240):  # Default to baseline revenue
    """Get complete waste summary for reporting"""
    csv_data = fetch_waste_data()
    if not csv_data:
        return None
    
    waste_data = parse_waste_csv(csv_data)
    metrics = calculate_waste_metrics(waste_data, monthly_revenue)
    
    return metrics

if __name__ == '__main__':
    print("Fetching waste management data...")
    summary = get_waste_summary()
    
    if summary:
        print(f"\n♻️ WASTE MANAGEMENT SUMMARY")
        print(f"Total Waste Value: IDR {summary['total_waste_value']:,.0f}")
        print(f"Total Items Wasted: {summary['total_items']}")
        print(f"Waste % of Revenue: {summary['waste_percentage']:.1f}%")
        print(f"\nBy Category:")
        for cat, data in summary['categories'].items():
            if data['count'] > 0:
                print(f"  {cat.title()}: {data['count']} items (IDR {data['cost']:,.0f})")
        print(f"\nTop Waste Items:")
        for item in summary['top_waste_items'][:3]:
            print(f"  - {item['item']}: IDR {item['cost']:,.0f} ({item['note']})")
    else:
        print("❌ Failed to get waste data")
