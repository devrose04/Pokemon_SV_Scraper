"""
Test script for Google Sheets API connection.
This script tests the connection to Google Sheets API and provides detailed error information.
"""

import os
import sys
import socket
import ssl
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def test_connection(credentials_file):
    """
    Test the connection to Google Sheets API.
    
    Args:
        credentials_file (str): Path to the Google API credentials JSON file
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        # Print Python and OpenSSL versions
        print(f"Python version: {sys.version}")
        print(f"OpenSSL version: {ssl.OPENSSL_VERSION}")
        
        # Check if credentials file exists
        if not os.path.exists(credentials_file):
            print(f"Error: Credentials file not found at {credentials_file}")
            return False
        
        # Set a longer timeout
        socket.setdefaulttimeout(60)
        
        print(f"Loading credentials from: {os.path.abspath(credentials_file)}")
        
        # Set up credentials
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=['https://www.googleapis.com/auth/spreadsheets', 
                   'https://www.googleapis.com/auth/drive']
        )
        
        print("Credentials loaded successfully")
        print(f"Service account email: {credentials.service_account_email}")
        
        # Build the services
        print("Building Google Sheets service...")
        sheets_service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
        
        print("Building Google Drive service...")
        drive_service = build('drive', 'v3', credentials=credentials, cache_discovery=False)
        
        # Test Drive API
        print("Testing Google Drive API...")
        drive_about = drive_service.about().get(fields="user").execute()
        print(f"Drive API connection successful: {drive_about}")
        
        # Create a test spreadsheet
        print("Creating a test spreadsheet...")
        spreadsheet_body = {
            'properties': {
                'title': 'API Connection Test'
            }
        }
        
        spreadsheet = sheets_service.spreadsheets().create(
            body=spreadsheet_body
        ).execute()
        
        spreadsheet_id = spreadsheet['spreadsheetId']
        print(f"Test spreadsheet created with ID: {spreadsheet_id}")
        
        # Clean up - delete the test spreadsheet
        print("Deleting test spreadsheet...")
        drive_service.files().delete(fileId=spreadsheet_id).execute()
        print("Test spreadsheet deleted")
        
        print("Connection test successful!")
        return True
        
    except HttpError as error:
        print(f"HTTP Error: {error.resp.status} {error.content.decode('utf-8')}")
        if error.resp.status == 403:
            print("\nPossible causes:")
            print("1. The Google Drive or Sheets API is not enabled for your project")
            print("2. Your service account doesn't have the necessary permissions")
            print("\nSolutions:")
            print("1. Go to https://console.cloud.google.com/apis/library")
            print("2. Enable both 'Google Drive API' and 'Google Sheets API'")
            print("3. Wait a few minutes for the changes to propagate")
        return False
    except socket.timeout:
        print("Error: Connection timed out")
        print("\nPossible causes:")
        print("1. Network connectivity issues")
        print("2. Firewall or proxy blocking the connection")
        print("\nSolutions:")
        print("1. Check your internet connection")
        print("2. Try a different network")
        print("3. Check firewall settings")
        return False
    except ConnectionError as e:
        print(f"Connection Error: {str(e)}")
        print("\nPossible causes:")
        print("1. Network connectivity issues")
        print("2. Firewall or proxy blocking the connection")
        print("\nSolutions:")
        print("1. Check your internet connection")
        print("2. Try a different network")
        print("3. Check firewall settings")
        return False
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        return False

def main():
    credentials_file = 'credentials.json'
    
    # Allow specifying a different credentials file
    if len(sys.argv) > 1:
        credentials_file = sys.argv[1]
    
    print(f"Testing connection to Google Sheets API with credentials file: {credentials_file}")
    
    if test_connection(credentials_file):
        print("\nConnection test PASSED!")
        return 0
    else:
        print("\nConnection test FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 