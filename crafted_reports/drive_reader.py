#!/usr/bin/env python3
"""
Crafted Daily Financial Report - Google Drive Reader
Read-only access to daily expenses and revenue data
"""

import os
import json
import pickle
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account

# Read-only scope for Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Path to service account credentials file
SERVICE_ACCOUNT_FILE = '/root/.openclaw/workspace/crafted_reports/service_account.json'

def get_drive_service():
    """Authenticate and return Google Drive service (read-only)"""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(
            f"Service account credentials not found at {SERVICE_ACCOUNT_FILE}. "
            "Please create a service account and download the JSON credentials."
        )
    
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    
    return build('drive', 'v3', credentials=credentials)

def get_sheets_service():
    """Authenticate and return Google Sheets service (read-only)"""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(
            f"Service account credentials not found at {SERVICE_ACCOUNT_FILE}."
        )
    
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )
    
    return build('sheets', 'v4', credentials=credentials)

def extract_spreadsheet_id(url):
    """Extract spreadsheet ID from Google Sheets URL"""
    # Handle different URL formats
    if '/d/' in url:
        parts = url.split('/d/')
        if len(parts) > 1:
            return parts[1].split('/')[0].split('?')[0]
    return None

def read_spreadsheet(spreadsheet_id, range_name='Sheet1'):
    """Read data from a Google Sheet"""
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        values = result.get('values', [])
        return values
    except Exception as e:
        return {'error': str(e)}

def list_drive_files(query=None, page_size=10):
    """List files in Google Drive (read-only)"""
    try:
        service = get_drive_service()
        
        params = {
            'pageSize': page_size,
            'fields': 'nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink)'
        }
        
        if query:
            params['q'] = query
            
        results = service.files().list(**params).execute()
        files = results.get('files', [])
        return files
    except Exception as e:
        return {'error': str(e)}

def get_file_metadata(file_id):
    """Get metadata for a specific file"""
    try:
        service = get_drive_service()
        file = service.files().get(
            fileId=file_id,
            fields='id, name, mimeType, modifiedTime, webViewLink, size'
        ).execute()
        return file
    except Exception as e:
        return {'error': str(e)}

def test_crafted_expenses_access():
    """Test access to the Crafted daily expenses spreadsheet"""
    url = 'https://docs.google.com/spreadsheets/d/1u7Du_KjwGvEL-Jp0oI91Zjlq8gYtxOx5/edit?usp=drivesdk&ouid=101241787498200223121&rtpof=true&sd=true'
    
    spreadsheet_id = extract_spreadsheet_id(url)
    
    if not spreadsheet_id:
        return {'error': 'Could not extract spreadsheet ID from URL'}
    
    print(f"Testing access to spreadsheet ID: {spreadsheet_id}")
    
    # Test 1: Check file metadata
    metadata = get_file_metadata(spreadsheet_id)
    if 'error' in metadata:
        return {
            'success': False,
            'stage': 'metadata_check',
            'error': metadata['error']
        }
    
    print(f"File name: {metadata.get('name')}")
    print(f"Last modified: {metadata.get('modifiedTime')}")
    
    # Test 2: Try to read the sheet data
    data = read_spreadsheet(spreadsheet_id)
    if 'error' in data:
        return {
            'success': False,
            'stage': 'data_read',
            'error': data['error']
        }
    
    return {
        'success': True,
        'metadata': metadata,
        'row_count': len(data),
        'sample_data': data[:5] if len(data) > 5 else data
    }

if __name__ == '__main__':
    result = test_crafted_expenses_access()
    print(json.dumps(result, indent=2, default=str))
