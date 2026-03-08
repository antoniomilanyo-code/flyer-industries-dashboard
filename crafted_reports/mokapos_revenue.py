#!/usr/bin/env python3
"""
Mokapos API Integration for Crafted Daily Revenue
Fetches daily sales data from Mokapos back office
"""

import requests
import os
from datetime import datetime, timedelta
from collections import defaultdict

MOKAPOS_BASE_URL = "https://api.mokapos.com"
MOKAPOS_LOGIN_URL = f"{MOKAPOS_BASE_URL}/v3/auth/login"
MOKAPOS_BUSINESSES_URL = f"{MOKAPOS_BASE_URL}/v3/businesses"

def get_credentials():
    """Read credentials from secure file"""
    creds_file = '/root/.openclaw/workspace/crafted_reports/.mokapos_credentials'
    email = None
    password = None
    
    if os.path.exists(creds_file):
        with open(creds_file, 'r') as f:
            for line in f:
                if line.startswith('EMAIL='):
                    email = line.split('=', 1)[1].strip()
                elif line.startswith('PASSWORD='):
                    password = line.split('=', 1)[1].strip()
    
    return email, password

def login_to_mokapos(email=None, password=None):
    """Authenticate with Mokapos and get access token"""
    if not email or not password:
        email, password = get_credentials()
    
    if not email or not password:
        return {'error': 'No credentials available'}
    
    try:
        payload = {
            'email': email,
            'password': password
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.post(MOKAPOS_LOGIN_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'access_token': data.get('access_token'),
                'refresh_token': data.get('refresh_token'),
                'user': data.get('user')
            }
        else:
            return {'error': f'Login failed: {response.status_code} - {response.text}'}
            
    except Exception as e:
        return {'error': f'Login exception: {str(e)}'}

def get_businesses(access_token):
    """Get list of businesses for the user"""
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        response = requests.get(MOKAPOS_BUSINESSES_URL, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f'Failed to get businesses: {response.status_code}'}
            
    except Exception as e:
        return {'error': str(e)}

def get_outlets(access_token, business_id):
    """Get outlets for a business"""
    try:
        url = f"{MOKAPOS_BASE_URL}/v3/businesses/{business_id}/outlets"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f'Failed to get outlets: {response.status_code}'}
            
    except Exception as e:
        return {'error': str(e)}

def get_sales_summary(access_token, outlet_id, date=None):
    """Get sales summary for an outlet on a specific date"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        url = f"{MOKAPOS_BASE_URL}/v2/outlets/{outlet_id}/sales_summary"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        params = {
            'date': date
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f'Failed to get sales summary: {response.status_code} - {response.text}'}
            
    except Exception as e:
        return {'error': str(e)}

def get_payments(access_token, outlet_id, date=None, page=1, per_page=100):
    """Get payments/transactions for an outlet"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        url = f"{MOKAPOS_BASE_URL}/v2/outlets/{outlet_id}/payments"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        params = {
            'date': date,
            'page': page,
            'per_page': per_page
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f'Failed to get payments: {response.status_code}'}
            
    except Exception as e:
        return {'error': str(e)}

def generate_revenue_summary(access_token, outlet_id=None, date=None):
    """Generate comprehensive revenue summary"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # Get sales summary
    sales_data = get_sales_summary(access_token, outlet_id, date)
    
    if isinstance(sales_data, dict) and 'error' in sales_data:
        return sales_data
    
    # Get payments for more detail
    payments_data = get_payments(access_token, outlet_id, date)
    
    # Parse and summarize
    summary = {
        'date': date,
        'gross_sales': 0,
        'net_sales': 0,
        'total_transactions': 0,
        'payment_methods': defaultdict(float),
        'categories': defaultdict(float),
        'discounts_total': 0,
        'taxes_total': 0,
        'gratuities_total': 0,
        'refunds_total': 0
    }
    
    # Extract from sales summary if available
    if 'data' in sales_data:
        data = sales_data['data']
        summary['gross_sales'] = data.get('gross_sales', 0)
        summary['net_sales'] = data.get('net_sales', 0)
        summary['discounts_total'] = data.get('discounts', 0)
        summary['taxes_total'] = data.get('taxes', 0)
        summary['gratuities_total'] = data.get('gratuities', 0)
        summary['total_transactions'] = data.get('transactions_count', 0)
    
    # Parse payments for payment methods
    if isinstance(payments_data, dict) and 'data' in payments_data:
        payments = payments_data['data'].get('payments', [])
        
        for payment in payments:
            # Payment methods
            payment_type = payment.get('payment_type', 'Unknown')
            total_collected = payment.get('total_collected', 0)
            summary['payment_methods'][payment_type] += total_collected
            
            # Check for refunds
            if payment.get('is_refunded', False) or payment.get('refund_amount', 0) > 0:
                summary['refunds_total'] += payment.get('refund_amount', 0)
            
            # Categories from checkouts
            checkouts = payment.get('checkouts', [])
            for checkout in checkouts:
                category = checkout.get('category_name', 'Unknown')
                net_sales = checkout.get('net_sales', 0)
                if net_sales > 0:
                    summary['categories'][category] += net_sales
    
    summary['payment_methods'] = dict(summary['payment_methods'])
    summary['categories'] = dict(summary['categories'])
    
    return summary

def format_revenue_report(summary):
    """Format revenue summary for display"""
    if isinstance(summary, dict) and 'error' in summary:
        return f"❌ Mokapos Error: {summary['error']}"
    
    report = []
    report.append("💵 *DAILY REVENUE (Mokapos)*")
    report.append(f"   Date: {summary['date']}")
    report.append("")
    report.append(f"   Gross Sales: Rp {summary['gross_sales']:,.0f}")
    report.append(f"   Net Sales: Rp {summary['net_sales']:,.0f}")
    report.append(f"   Transactions: {summary['total_transactions']}")
    report.append("")
    
    if summary['discounts_total'] > 0:
        report.append(f"   Discounts: -Rp {summary['discounts_total']:,.0f}")
    if summary['taxes_total'] > 0:
        report.append(f"   Taxes: Rp {summary['taxes_total']:,.0f}")
    if summary['gratuities_total'] > 0:
        report.append(f"   Service/Gratuities: Rp {summary['gratuities_total']:,.0f}")
    if summary['refunds_total'] > 0:
        report.append(f"   Refunds: -Rp {summary['refunds_total']:,.0f}")
    
    if summary['payment_methods']:
        report.append("")
        report.append("   Payment Methods:")
        for method, amount in sorted(summary['payment_methods'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"      • {method}: Rp {amount:,.0f}")
    
    if summary['categories']:
        report.append("")
        report.append("   Top Categories:")
        for cat, amount in sorted(summary['categories'].items(), key=lambda x: x[1], reverse=True)[:5]:
            report.append(f"      • {cat}: Rp {amount:,.0f}")
    
    return "\n".join(report)

def get_crafted_revenue(date=None):
    """Main function to get Crafted's daily revenue"""
    print("Authenticating with Mokapos...")
    
    # Login
    auth = login_to_mokapos()
    if 'error' in auth:
        return auth
    
    access_token = auth.get('access_token')
    
    print("Getting businesses...")
    businesses = get_businesses(access_token)
    
    if isinstance(businesses, dict) and 'error' in businesses:
        return businesses
    
    # Find Crafted business (should be in the list)
    crafted_business = None
    for biz in businesses.get('data', []):
        if 'craft' in biz.get('name', '').lower() or 'crafted' in biz.get('name', '').lower():
            crafted_business = biz
            break
    
    if not crafted_business:
        # Use first business if Crafted not found by name
        if businesses.get('data'):
            crafted_business = businesses['data'][0]
    
    if not crafted_business:
        return {'error': 'No business found'}
    
    business_id = crafted_business.get('id')
    print(f"Found business: {crafted_business.get('name')} (ID: {business_id})")
    
    # Get outlets
    print("Getting outlets...")
    outlets = get_outlets(access_token, business_id)
    
    if isinstance(outlets, dict) and 'error' in outlets:
        return outlets
    
    if not outlets.get('data'):
        return {'error': 'No outlets found'}
    
    # Use first outlet
    outlet = outlets['data'][0]
    outlet_id = outlet.get('id')
    print(f"Using outlet: {outlet.get('name')} (ID: {outlet_id})")
    
    # Generate revenue summary
    print("Fetching revenue data...")
    summary = generate_revenue_summary(access_token, outlet_id, date)
    
    return summary

if __name__ == '__main__':
    summary = get_crafted_revenue()
    report = format_revenue_report(summary)
    print(report)
