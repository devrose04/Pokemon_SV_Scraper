"""
Script to help create a credentials.json file for Google Sheets API.
This script will guide the user through the process of creating a credentials.json file.
"""

import os
import json
import shutil

def main():
    print("Google Sheets API Credentials Setup")
    print("===================================")
    print("This script will help you create a credentials.json file for Google Sheets API.")
    print("You need to have a Google Cloud project with the Google Sheets API enabled.")
    print("You also need to have a service account with the appropriate permissions.")
    print("\nFollow these steps:")
    print("1. Go to the Google Cloud Console (https://console.cloud.google.com/)")
    print("2. Create a new project")
    print("3. Enable the Google Sheets API and Google Drive API")
    print("4. Create a service account")
    print("5. Download the JSON key file")
    print("6. Share your Google Spreadsheet with the service account email address")
    print("\nOnce you have downloaded the JSON key file, you can either:")
    print("1. Rename it to credentials.json and place it in this directory")
    print("2. Enter the path to the file when prompted by this script")
    
    # Check if credentials.json already exists
    if os.path.exists('credentials.json'):
        print("\nA credentials.json file already exists in this directory.")
        overwrite = input("Do you want to overwrite it? (y/n): ")
        if overwrite.lower() != 'y':
            print("Operation cancelled.")
            return
    
    # Check if credentials_template.json exists
    if not os.path.exists('credentials_template.json'):
        print("\nError: credentials_template.json file not found.")
        print("This file is required to create a new credentials.json file.")
        return
    
    # Ask the user for the path to the JSON key file
    print("\nPlease enter the path to the JSON key file you downloaded from Google Cloud Console.")
    print("Or press Enter to manually enter the credentials information.")
    json_path = input("Path to JSON key file: ")
    
    if json_path and os.path.exists(json_path):
        # Copy the JSON key file to credentials.json
        shutil.copy(json_path, 'credentials.json')
        print("\nCredentials file created successfully!")
        print("You can now use the --upload flag with the main.py script.")
    else:
        # Create a new credentials.json file based on the template
        with open('credentials_template.json', 'r') as f:
            template = json.load(f)
        
        print("\nPlease enter the following information:")
        template['project_id'] = input("Project ID: ")
        template['private_key_id'] = input("Private Key ID: ")
        template['private_key'] = input("Private Key (including BEGIN/END lines): ")
        template['client_email'] = input("Client Email: ")
        template['client_id'] = input("Client ID: ")
        template['client_x509_cert_url'] = input("Client X509 Cert URL: ")
        
        # Save the credentials.json file
        with open('credentials.json', 'w') as f:
            json.dump(template, f, indent=2)
        
        print("\nCredentials file created successfully!")
        print("You can now use the --upload flag with the main.py script.")
    
    # Remind the user to share the spreadsheet
    print("\nRemember to share your Google Spreadsheet with the service account email address:")
    if 'client_email' in locals():
        print(f"  {template['client_email']}")
    else:
        print("  (check the client_email field in your credentials.json file)")

if __name__ == "__main__":
    main() 