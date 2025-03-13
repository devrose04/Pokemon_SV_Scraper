"""
Test script for Google Sheets integration.
This script checks if the credentials file exists and if the Google Sheets API is accessible.
"""

import os
import sys
from sheets_uploader import upload_to_sheets

def main():
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("Error: credentials.json file not found.")
        print("Please create a credentials.json file with your Google API credentials.")
        print("You can use the credentials_template.json file as a template.")
        print("\nTo set up Google Cloud credentials:")
        print("1. Go to the Google Cloud Console (https://console.cloud.google.com/)")
        print("2. Create a new project")
        print("3. Enable the Google Sheets API and Google Drive API")
        print("4. Create a service account")
        print("5. Download the JSON key file and rename it to credentials.json")
        print("6. Share your Google Spreadsheet with the service account email address")
        return 1
    
    # Check if trainer_data.json exists
    if not os.path.exists('trainer_data.json'):
        print("Error: trainer_data.json file not found.")
        print("Please run the main.py script first to generate the data.")
        return 1
    
    # Try to upload to Google Sheets
    try:
        print("Testing Google Sheets integration...")
        upload_to_sheets('trainer_data.json', 'Pokemon SV Trainer Data Test')
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 