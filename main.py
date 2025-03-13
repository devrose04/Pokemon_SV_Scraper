import json
import time
import argparse
import requests
from bs4 import BeautifulSoup

# Import the upload_to_sheets function if the required packages are installed
try:
    from sheets_uploader import upload_to_sheets
    SHEETS_AVAILABLE = True
except ImportError:
    SHEETS_AVAILABLE = False

def get_trainer_urls(base_url):
    response = requests.get(base_url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all links in the table
    links = soup.select("table.table tbody tr td:first-child a")
    trainer_urls = [link.get('href') for link in links if link.get('href')]
    
    return trainer_urls

def parse_trainer_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get the page title as trainer name
        trainer_name = soup.title.text if soup.title else "Unknown"
        
        # Get the URL as rank and rating (since we can't get these from external blogs)
        rank = "N/A"
        rating = "N/A"
        
        # Try to extract rank and rating from the title if available
        # Format is often like "[S27最終7位]" or similar
        if trainer_name:
            import re
            rank_match = re.search(r'S\d+最終(\d+)位', trainer_name)
            if rank_match:
                rank = rank_match.group(1)
            
            rating_match = re.search(r'レート(\d+)', trainer_name)
            if rating_match:
                rating = rating_match.group(1)
        
        # Try to find Pokémon names in the page
        html = response.text
        pokemon_names = []
        
        # Common Pokémon names in Japanese
        common_pokemon = [
            "ウインディ", "カイリュー", "ガブリアス", "キュウコン", "ギャラドス", "グレイシア", 
            "ゲンガー", "ゴリランダー", "サーフゴー", "サンダース", "ジバコイル", "シャワーズ", 
            "ジュラルドン", "スイクン", "ゼラオラ", "ソルガレオ", "ディアルガ", "テツノドクガ", 
            "テツノブジン", "ドラパルト", "ドリュウズ", "ナットレイ", "ニンフィア", "ハガネール", 
            "パルキア", "ヒードラン", "ブースター", "フシギバナ", "ブラッキー", "ブリザポス", 
            "ヘイラッシャ", "ボーマンダ", "ポリゴン2", "ポリゴンZ", "マニューラ", "ミミッキュ", 
            "メタグロス", "ユキノオー", "ラウドボーン", "ラグラージ", "ランドロス", "リザードン", 
            "ルカリオ", "レックウザ", "ロトム"
        ]
        
        # Look for these Pokémon names in the text
        for pokemon in common_pokemon:
            if pokemon in html:
                pokemon_names.append(pokemon)
        
        # Deduplicate and take up to 6
        pokemon_names = list(set(pokemon_names))[:6]
        
        # Create Pokémon data
        pokemon_data = []
        for name in pokemon_names:
            pokemon_data.append({
                "name": name,
                "ability": "不明",  # Unknown
                "item": "不明",     # Unknown
                "tera_type": "不明", # Unknown
                "nature": "不明",    # Unknown
                "moves": ["不明"],   # Unknown
                "evs": {
                    "H": "0",
                    "A": "0",
                    "B": "0",
                    "C": "0",
                    "D": "0",
                    "S": "0"
                }
            })
        
        return {
            "trainer_name": trainer_name,
            "rank": rank,
            "rating": rating,
            "pokemon": pokemon_data,
            "url": url
        }
        
    except Exception as e:
        print(f"Error parsing page: {str(e)}")
        return {
            "trainer_name": f"Error: {url}",
            "rank": "N/A",
            "rating": "N/A",
            "pokemon": [],
            "url": url
        }

def main():
    parser = argparse.ArgumentParser(description='Scrape Pokémon SV trainer data')
    parser.add_argument('--limit', type=int, default=10, help='Limit the number of trainers to scrape (0 for all)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests in seconds')
    parser.add_argument('--output', default='trainer_data.json', help='Output JSON file')
    parser.add_argument('--upload', action='store_true', help='Upload data to Google Sheets')
    parser.add_argument('--spreadsheet', default='Pokemon SV Trainer Data', help='Name of the Google Spreadsheet')
    parser.add_argument('--credentials', default='credentials.json', help='Path to the Google API credentials file')
    
    args = parser.parse_args()
    
    try:
        # Base URL for the trainer list
        base_url = "https://sv.pokedb.tokyo/trainer/list?season=27&rule=0&party=1"
        
        # Get trainer URLs
        print("Getting trainer URLs...")
        trainer_urls = get_trainer_urls(base_url)
        print(f"Found {len(trainer_urls)} trainer URLs")
        
        # Limit the number of trainers if specified
        if args.limit > 0:
            trainer_urls = trainer_urls[:args.limit]
            print(f"Limited to {args.limit} trainers")
        
        # Parse each trainer page
        all_trainer_data = []
        for i, url in enumerate(trainer_urls):
            print(f"Parsing trainer {i+1}/{len(trainer_urls)}: {url}")
            trainer_data = parse_trainer_page(url)
            all_trainer_data.append(trainer_data)
            
            # Add a delay to avoid overloading the server
            if i < len(trainer_urls) - 1:  # No need to delay after the last request
                time.sleep(args.delay)
        
        # Save the data to a JSON file
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(all_trainer_data, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully scraped {len(all_trainer_data)} trainer pages")
        print(f"Data saved to {args.output}")
        
        # Upload to Google Sheets if requested
        if args.upload:
            if SHEETS_AVAILABLE:
                print("Uploading data to Google Sheets...")
                upload_to_sheets(args.output, args.spreadsheet, args.credentials)
            else:
                print("Error: Google Sheets integration is not available. Please install the required packages:")
                print("pip install gspread oauth2client")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 