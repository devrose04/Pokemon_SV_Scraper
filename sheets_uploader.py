import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def upload_to_sheets(json_file_path, spreadsheet_name, credentials_file):
    """
    Upload JSON data to Google Sheets
    
    Args:
        json_file_path (str): Path to the JSON data file to upload
        spreadsheet_name (str): Name of the Google Sheets document
        credentials_file (str): Path to the Google API credentials JSON file
    
    Returns:
        str: Spreadsheet ID if successful, None otherwise
    """
    try:
        # Verify files exist
        if not os.path.exists(credentials_file):
            print(f"Error: Credentials file not found at {credentials_file}")
            return None
            
        if not os.path.exists(json_file_path):
            print(f"Error: JSON data file not found at {json_file_path}")
            return None
        
        # Load JSON data
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Set up credentials
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=['https://www.googleapis.com/auth/spreadsheets', 
                   'https://www.googleapis.com/auth/drive']
        )
        
        # Build the services
        sheets_service = build('sheets', 'v4', credentials=credentials)
        drive_service = build('drive', 'v3', credentials=credentials)
        
        # Check if spreadsheet already exists
        results = drive_service.files().list(
            q=f"name='{spreadsheet_name}' and mimeType='application/vnd.google-apps.spreadsheet'",
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        files = results.get('files', [])
        
        # Handle existing or new spreadsheet
        if files:
            # Use existing spreadsheet
            spreadsheet_id = files[0]['id']
            print(f"Found existing spreadsheet: {spreadsheet_name} (ID: {spreadsheet_id})")
            
            # Get information about existing sheets
            spreadsheet_info = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = spreadsheet_info.get('sheets', [])
            
            if sheets:
                # Use the first sheet - clear it instead of deleting
                first_sheet = sheets[0]
                sheet_id = first_sheet['properties']['sheetId']
                sheet_title = first_sheet['properties']['title']
                
                # Clear the sheet content
                sheets_service.spreadsheets().values().clear(
                    spreadsheetId=spreadsheet_id,
                    range=sheet_title
                ).execute()
                
                # Rename the sheet if it's not already named "Trainer Data"
                if sheet_title != "Trainer Data":
                    sheets_service.spreadsheets().batchUpdate(
                        spreadsheetId=spreadsheet_id,
                        body={
                            "requests": [{
                                "updateSheetProperties": {
                                    "properties": {
                                        "sheetId": sheet_id,
                                        "title": "Trainer Data"
                                    },
                                    "fields": "title"
                                }
                            }]
                        }
                    ).execute()
                    sheet_title = "Trainer Data"
                
                # Delete any additional sheets (if there are more than one)
                if len(sheets) > 1:
                    batch_requests = []
                    for sheet in sheets[1:]:  # Skip the first sheet
                        batch_requests.append({
                            "deleteSheet": {
                                "sheetId": sheet['properties']['sheetId']
                            }
                        })
                    
                    if batch_requests:
                        sheets_service.spreadsheets().batchUpdate(
                            spreadsheetId=spreadsheet_id,
                            body={"requests": batch_requests}
                        ).execute()
            else:
                # This shouldn't happen, but just in case
                print("Error: Spreadsheet exists but has no sheets")
                return None
                
        else:
            # Create a new spreadsheet with a custom sheet name
            spreadsheet_body = {
                'properties': {
                    'title': spreadsheet_name
                },
                'sheets': [{
                    'properties': {
                        'title': 'Trainer Data'
                    }
                }]
            }
            
            spreadsheet = sheets_service.spreadsheets().create(
                body=spreadsheet_body
            ).execute()
            
            spreadsheet_id = spreadsheet['spreadsheetId']
            sheet_title = "Trainer Data"
            print(f"Created new spreadsheet: {spreadsheet_name} (ID: {spreadsheet_id})")
        
        # Prepare data for upload
        if not data:
            print("Warning: No data to upload (empty JSON)")
            return spreadsheet_id
            
        # Convert data to a format suitable for Sheets
        if isinstance(data, list) and len(data) > 0:
            # Get headers from the first item
            headers = list(data[0].keys())
            
            # Create values array with headers as first row
            values = [headers]
            
            # Add data rows
            for item in data:
                row = [item.get(header, '') for header in headers]
                values.append(row)
                
        elif isinstance(data, dict):
            # Handle dictionary data
            headers = list(data.keys())
            values = [headers, list(data.values())]
        else:
            print(f"Error: Unsupported data format. Expected list or dict, got {type(data)}")
            return None
        
        # Upload the data
        result = sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"Trainer Data!A1",
            valueInputOption="RAW",
            body={"values": values}
        ).execute()
        
        # Format the header row (make it bold)
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "requests": [{
                    "repeatCell": {
                        "range": {
                            "sheetId": 0,
                            "startRowIndex": 0,
                            "endRowIndex": 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {
                                    "bold": True
                                }
                            }
                        },
                        "fields": "userEnteredFormat.textFormat.bold"
                    }
                }]
            }
        ).execute()
        
        print(f"Successfully uploaded data to Google Sheets: {len(values)-1} rows of data")
        print(f"Spreadsheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        return spreadsheet_id
        
    except HttpError as error:
        print(f"Error uploading to Google Sheets: {error.resp.status} {error.content.decode('utf-8')}")
        return None
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    upload_to_sheets(
        "trainer_data.json",
        "Pokemon SV Trainer Data",
        "credentials.json"
    ) 