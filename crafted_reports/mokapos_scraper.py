#!/usr/bin/env python3
"""
Mokapos Web Dashboard Scraper
Fetches daily sales data from Mokapos back office web interface
"""

import requests
import os
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict

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

class MokaposScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json'
        })
        self.base_url = "https://backoffice.mokapos.com"
        self.access_token = None
        
    def login(self, email=None, password=None):
        """Login to Mokapos web dashboard"""
        if not email or not password:
            email, password = get_credentials()
        
        if not email or not password:
            return {'error': 'No credentials available'}
        
        try:
            # First, get CSRF token or any required cookies
            print("Getting login page...")
            login_page = self.session.get(f"{self.base_url}/login", timeout=30)
            
            # Try the login API
            login_url = f"{self.base_url}/api/v3/auth/login"
            payload = {
                'email': email,
                'password': password
            }
            
            print(f"Attempting login to {login_url}...")
            response = self.session.post(login_url, json=payload, timeout=30)
            
            print(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                if self.access_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}'
                    })
                    return {'success': True, 'user': data.get('user')}
                else:
                    return {'error': 'No access token in response', 'data': data}
            else:
                # Try to parse error
                try:
                    error_data = response.json()
                    return {'error': f'Login failed: {response.status_code}', 'details': error_data}
                except:
                    return {'error': f'Login failed: {response.status_code}', 'response': response.text[:500]}
                    
        except Exception as e:
            return {'error': f'Login exception: {str(e)}'}
    
    def get_businesses(self):
        """Get list of businesses"""
        try:
            url = f"{self.base_url}/api/v3/businesses"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'Failed to get businesses: {response.status_code}'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def get_outlets(self, business_id):
        """Get outlets for a business"""
        try:
            url = f"{self.base_url}/api/v3/businesses/{business_id}/outlets"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'Failed to get outlets: {response.status_code}'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def get_sales_summary(self, outlet_id, date=None):
        """Get sales summary for an outlet"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Try v2 API endpoint
            url = f"{self.base_url}/api/v2/outlets/{outlet_id}/sales_summary"
            params = {'date': date}
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                # Try alternative endpoint
                url = f"{self.base_url}/api/v3/outlets/{outlet_id}/sales_summary"
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {'error': f'Failed to get sales summary: {response.status_code}', 'text': response.text[:200]}
                
        except Exception as e:
            return {'error': str(e)}
    
    def get_daily_report(self, outlet_id, date=None):
        """Get daily report data"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            url = f"{self.base_url}/api/v2/outlets/{outlet_id}/reports/daily"
            params = {'date': date}
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'Failed to get daily report: {response.status_code}'}
                
        except Exception as e:
            return {'error': str(e)}

def get_crafted_revenue(date=None):
    """Main function to get Crafted's daily revenue"""
    scraper = MokaposScraper()
    
    print("Logging in to Mokapos...")
    login_result = scraper.login()
    
    if 'error' in login_result:
        return login_result
    
    print("Login successful!")
    print("Getting businesses...")
    
    businesses = scraper.get_businesses()
    
    if isinstance(businesses, dict) and 'error' in businesses:
        return businesses
    
    # Find Crafted business
    crafted_business = None
    for biz in businesses.get('data', []):
        name = biz.get('name', '').lower()
        if 'craft' in name or 'crafted' in name:
            crafted_business = biz
            break
    
    if not crafted_business and businesses.get('data'):
        # Use first business
        crafted_business = businesses['data'][0]
    
    if not crafted_business:
        return {'error': 'No business found'}
    
    business_id = crafted_business.get('id')
    business_name = crafted_business.get('name')
    print(f"Found business: {business_name} (ID: {business_id})")
    
    # Get outlets
    print("Getting outlets...")
    outlets = scraper.get_outlets(business_id)
    
    if isinstance(outlets, dict) and 'error' in outlets:
        return outlets
    
    if not outlets.get('data'):
        return {'error': 'No outlets found'}
    
    outlet = outlets['data'][0]
    outlet_id = outlet.get('id')
    outlet_name = outlet.get('name')
    print(f"Using outlet: {outlet_name} (ID: {outlet_id})")
    
    # Get sales summary
    print("Fetching sales summary...")
    sales_data = scraper.get_sales_summary(outlet_id, date)
    
    return sales_data

def format_revenue_report(data):
    """Format revenue data for display"""
    if isinstance(data, dict) and 'error' in data:
        return f"❌ Mokapos Error: {data['error']}"
    
    if 'data' not in data:
        return f"❌ No data available. Response: {json.dumps(data, indent=2)[:500]}"
    
    report = []
    report.append("💵 *DAILY REVENUE (Mokapos)*")
    report.append("")
    
    d = data['data']
    
    report.append(f"   Gross Sales: Rp {d.get('gross_sales', 0):,.0f}")
    report.append(f"   Net Sales: Rp {d.get('net_sales', 0):,.0f}")
    report.append(f"   Transactions: {d.get('transactions_count', 0)}")
    report.append("")
    
    if d.get('discounts', 0) > 0:
        report.append(f"   Discounts: -Rp {d['discounts']:,.0f}")
    if d.get('taxes', 0) > 0:
        report.append(f"   Taxes: Rp {d['taxes']:,.0f}")
    if d.get('gratuities', 0) > 0:
        report.append(f"   Gratuities: Rp {d['gratuities']:,.0f}")
    
    # Payment methods if available
    payments = d.get('payments', {})
    if payments:
        report.append("")
        report.append("   Payment Methods:")
        for method, amount in payments.items():
            report.append(f"      • {method}: Rp {amount:,.0f}")
    
    return "\n".join(report)

if __name__ == '__main__':
    data = get_crafted_revenue()
    report = format_revenue_report(data)
    print(report)
