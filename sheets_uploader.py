import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def upload_to_sheets(json_file, spreadsheet_name, credentials_file='credentials.json'):
    """
    Upload data from a JSON file to a Google Spreadsheet.
    
    Args:
        json_file (str): Path to the JSON file containing the data
        spreadsheet_name (str): Name of the Google Spreadsheet
        credentials_file (str): Path to the Google API credentials file
    """
    try:
        # Load the trainer data from the JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            trainer_data = json.load(f)
        
        # Set up the credentials for the Google Sheets API
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
        client = gspread.authorize(credentials)
        
        # Open the spreadsheet (create it if it doesn't exist)
        try:
            spreadsheet = client.open(spreadsheet_name)
        except gspread.exceptions.SpreadsheetNotFound:
            spreadsheet = client.create(spreadsheet_name)
            print(f"Created new spreadsheet: {spreadsheet_name}")
        
        # Clear existing worksheets
        for worksheet in spreadsheet.worksheets():
            spreadsheet.del_worksheet(worksheet)
        
        # Create the main worksheet for trainer data
        main_worksheet = spreadsheet.add_worksheet(title="Trainer Data", rows=len(trainer_data)+1, cols=10)
        
        # Set up the header row
        headers = ["Trainer Name", "Rank", "Rating", "URL", "Pokemon Count", "Pokemon Names"]
        main_worksheet.update('A1:F1', [headers])
        
        # Format the header row
        main_worksheet.format('A1:F1', {
            'textFormat': {'bold': True},
            'horizontalAlignment': 'CENTER',
            'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8}
        })
        
        # Prepare the data for the main worksheet
        main_data = []
        for trainer in trainer_data:
            pokemon_names = ", ".join([p["name"] for p in trainer["pokemon"]])
            main_data.append([
                trainer["trainer_name"],
                trainer["rank"],
                trainer["rating"],
                trainer["url"],
                len(trainer["pokemon"]),
                pokemon_names
            ])
        
        # Update the main worksheet with the data
        if main_data:
            main_worksheet.update(f'A2:F{len(main_data)+1}', main_data)
        
        # Create a detailed worksheet for Pokémon data
        pokemon_worksheet = spreadsheet.add_worksheet(title="Pokemon Details", rows=1000, cols=15)
        
        # Set up the header row for the Pokémon worksheet
        pokemon_headers = ["Trainer Name", "Pokemon Name", "Ability", "Item", "Tera Type", 
                          "Nature", "Moves", "HP", "Atk", "Def", "SpA", "SpD", "Spe"]
        pokemon_worksheet.update('A1:M1', [pokemon_headers])
        
        # Format the header row
        pokemon_worksheet.format('A1:M1', {
            'textFormat': {'bold': True},
            'horizontalAlignment': 'CENTER',
            'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8}
        })
        
        # Prepare the data for the Pokémon worksheet
        pokemon_data = []
        for trainer in trainer_data:
            for pokemon in trainer["pokemon"]:
                moves_str = ", ".join(pokemon["moves"])
                pokemon_data.append([
                    trainer["trainer_name"],
                    pokemon["name"],
                    pokemon["ability"],
                    pokemon["item"],
                    pokemon["tera_type"],
                    pokemon["nature"],
                    moves_str,
                    pokemon["evs"]["H"],
                    pokemon["evs"]["A"],
                    pokemon["evs"]["B"],
                    pokemon["evs"]["C"],
                    pokemon["evs"]["D"],
                    pokemon["evs"]["S"]
                ])
        
        # Update the Pokémon worksheet with the data
        if pokemon_data:
            pokemon_worksheet.update(f'A2:M{len(pokemon_data)+1}', pokemon_data)
        
        # Resize columns to fit content
        for worksheet in [main_worksheet, pokemon_worksheet]:
            for i in range(1, worksheet.col_count + 1):
                worksheet.columns_auto_resize(i-1, i)
        
        print(f"Successfully uploaded data to Google Spreadsheet: {spreadsheet_name}")
        print(f"Spreadsheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")
        
    except Exception as e:
        print(f"Error uploading to Google Sheets: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload trainer data to Google Sheets')
    parser.add_argument('--json', default='trainer_data.json', help='Path to the JSON file')
    parser.add_argument('--spreadsheet', default='Pokemon SV Trainer Data', help='Name of the Google Spreadsheet')
    parser.add_argument('--credentials', default='credentials.json', help='Path to the Google API credentials file')
    
    args = parser.parse_args()
    
    upload_to_sheets(args.json, args.spreadsheet, args.credentials) 