import json
import os
import socket
import sys
import time
import tkinter as tk
from tkinter import messagebox
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def show_message(message, is_error=False):
    """Show a message box instead of using input() for GUI applications"""
    try:
        # Only create root if it doesn't exist
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        if is_error:
            messagebox.showerror("Error", message)
        else:
            messagebox.showinfo("Information", message)
            
        root.destroy()
    except Exception as e:
        # Fallback to console if tkinter fails
        print(message)
        try:
            input("Press Enter to continue...")
        except:
            pass

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def safe_api_call(func, error_message="API call failed", max_retries=2):
    """
    Safely execute an API call with retry logic
    
    Args:
        func: Function to call
        error_message: Message to display on error
        max_retries: Maximum number of retry attempts
        
    Returns:
        The result of the function call, or None if it fails
    """
    for attempt in range(max_retries + 1):
        try:
            return func()
        except (ConnectionResetError, socket.timeout) as e:
            if attempt < max_retries:
                wait_time = 2 ** attempt
                print(f"Connection error: {str(e)}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"{error_message}: {str(e)}")
                return None
        except Exception as e:
            print(f"{error_message}: {type(e).__name__}: {str(e)}")
            return None

def upload_to_sheets(json_file_path, spreadsheet_name, credentials_file, spreadsheet_id=None):
    """
    Upload JSON data to Google Sheets
    
    Args:
        json_file_path (str): Path to the JSON data file to upload
        spreadsheet_name (str): Name of the Google Sheets document
        credentials_file (str): Path to the Google API credentials JSON file
        spreadsheet_id (str, optional): Specific Google Sheets ID to use
    
    Returns:
        str: Spreadsheet ID if successful, None otherwise
    """
    try:
        # Set a longer timeout for socket operations
        socket.setdefaulttimeout(60)
        
        # Get absolute paths for resources
        json_file_path = get_resource_path(json_file_path)
        credentials_file = get_resource_path(credentials_file)
        
        # Verify files exist
        if not os.path.exists(credentials_file):
            error_msg = f"Error: credentials.json not found at {credentials_file}"
            print(error_msg)
            show_message(error_msg, is_error=True)
            return None
            
        if not os.path.exists(json_file_path):
            error_msg = f"Error: trainer_data.json not found at {json_file_path}"
            print(error_msg)
            show_message(error_msg, is_error=True)
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
        
        # Build the services with cache_discovery=False to avoid connection issues
        sheets_service = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
        
        # If spreadsheet_id is provided, use it directly
        if spreadsheet_id:
            print(f"Using provided spreadsheet ID: {spreadsheet_id}")
            try:
                # Verify the spreadsheet exists and is accessible
                spreadsheet_info = safe_api_call(
                    lambda: sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute(),
                    "Error accessing specified spreadsheet"
                )
                if spreadsheet_info is None:
                    error_msg = f"Error: Could not access spreadsheet with ID {spreadsheet_id}"
                    print(error_msg)
                    show_message(error_msg, is_error=True)
                    return None
                
                # Use the specified sheet name
                sheet_name = "BaBa_kohsi様_入力シート"
                print(f"Using sheet: {sheet_name}")
                
            except Exception as e:
                error_msg = f"Error accessing spreadsheet: {str(e)}"
                print(error_msg)
                show_message(error_msg, is_error=True)
                return None
        
        # Prepare data for upload
        if not data or not isinstance(data, list) or len(data) == 0:
            warning_msg = "Warning: No data to upload or invalid data format"
            print(warning_msg)
            show_message(warning_msg, is_error=True)
            return spreadsheet_id
        
        # Prepare data rows
        headers = ["rank", "rating", "name", "article_url"]
        for i in range(1, 7):  # For 6 Pokemon
            pokemon_prefix = f"pokemon{i}_"
            headers.extend([
                f"{pokemon_prefix}name",
                f"{pokemon_prefix}item",
                f"{pokemon_prefix}nature",
                f"{pokemon_prefix}ability",
                f"{pokemon_prefix}Ttype",
                f"{pokemon_prefix}moves",
                f"{pokemon_prefix}effort"
            ])
        
        rows = [headers]
        
        # Process each trainer
        for trainer in data:
            row = [
                trainer.get("rank", ""),
                trainer.get("rating", ""),
                trainer.get("trainer_name", ""),
                trainer.get("article_url", "")
            ]
            
            # Add Pokemon data
            pokemon_list = trainer.get("pokemon", [])
            for i in range(6):  # Always process 6 slots
                if i < len(pokemon_list):
                    pokemon = pokemon_list[i]
                    moves_str = ", ".join(pokemon.get("moves", []))
                    evs = pokemon.get("evs", {})
                    effort_str = f"H{evs.get('H', '0')}, A{evs.get('A', '0')}, B{evs.get('B', '0')}, C{evs.get('C', '0')}, D{evs.get('D', '0')}, S{evs.get('S', '0')}"
                    
                    row.extend([
                        pokemon.get("name", ""),
                        pokemon.get("item", ""),
                        pokemon.get("nature", ""),
                        pokemon.get("ability", ""),
                        pokemon.get("tera_type", ""),
                        moves_str,
                        effort_str
                    ])
                else:
                    # Fill empty slots
                    row.extend([""] * 7)  # 7 fields per Pokemon
            
            rows.append(row)
        
        # Upload data
        result = safe_api_call(
            lambda: sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f"'{sheet_name}'!A1",
                valueInputOption="RAW",
                body={"values": rows}
            ).execute(),
            "Error uploading data"
        )
        
        if result is None:
            show_message("Error uploading data to Google Sheets", is_error=True)
            return None
            
        success_msg = f"Successfully uploaded {len(rows)-1} entries to the spreadsheet\nSpreadsheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        print(success_msg)
        show_message(success_msg)
        return spreadsheet_id
        
    except HttpError as error:
        error_msg = f"Error uploading to Google Sheets: {error.resp.status} {error.content.decode('utf-8')}"
        print(error_msg)
        show_message(error_msg, is_error=True)
        return None
    except Exception as e:
        error_msg = f"Error: {type(e).__name__}: {str(e)}"
        print(error_msg)
        show_message(error_msg, is_error=True)
        return None

# Example usage
if __name__ == "__main__":
    SPREADSHEET_ID = "1wiBHSCdacFaPJoYV17C1OzLe-MitprC8dtrb7hh4wZY"  # Your specific spreadsheet ID
    upload_to_sheets(
        "trainer_data.json",
        "Pokemon SV Trainer Data",
        "credentials.json",
        spreadsheet_id=SPREADSHEET_ID
    )