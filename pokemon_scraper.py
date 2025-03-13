import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random

class PokemonSVScraper:
    def __init__(self):
        self.base_url = "https://sv.pokedb.tokyo"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        })

    def get_trainers_with_articles(self, season=27, rule=0, party=1):
        """Get list of trainers who have published construction articles"""
        trainers = []
        page = 1
        
        while True:
            url = f"{self.base_url}/trainer/list"
            params = {
                'season': season,
                'rule': rule,
                'party': party,
                'page': page
            }
            
            try:
                print(f"Fetching page {page} of trainer list...")
                response = self.session.get(url, params=params)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all trainer rows in the table
                trainer_rows = soup.select('tr')
                
                if not trainer_rows:
                    print("No trainer rows found on this page")
                    break
                
                found_article = False
                for row in trainer_rows:
                    # Look for the "構築記事" link in the row
                    article_link = row.select_one('a:-soup-contains("構築記事")')
                    if not article_link:
                        continue
                        
                    found_article = True
                    
                    # Extract trainer data
                    cells = row.select('td')
                    if len(cells) >= 3:
                        rank_text = cells[0].get_text(strip=True)
                        # Extract only the numeric part of the rank
                        rank_match = re.search(r'(\d+)', rank_text)
                        if not rank_match:
                            continue
                            
                        rank = rank_match.group(1)
                        rating = cells[1].get_text(strip=True)
                        
                        # Find trainer name and URL
                        trainer_cell = cells[2]
                        trainer_text = trainer_cell.get_text(strip=True)
                        # Extract trainer name (remove the "構築記事" text)
                        trainer_name = trainer_text.replace("構築記事", "").strip()
                        
                        # Get article URL
                        article_url = article_link.get('href')
                        
                        # Find Pokemon links
                        pokemon_links = trainer_cell.select('a[href*="/pokemon/show/"]')
                        pokemon_ids = []
                        for link in pokemon_links:
                            pokemon_id = re.search(r'/pokemon/show/(\d{4}-\d{2})', link['href'])
                            if pokemon_id:
                                pokemon_ids.append(pokemon_id.group(1))
                        
                        if pokemon_ids:  # Only add trainers with visible Pokemon
                            trainers.append({
                                'rank': int(rank),
                                'rating': int(rating),
                                'trainer_name': trainer_name,
                                'article_url': article_url,
                                'pokemon_ids': pokemon_ids
                            })
                            print(f"Found trainer with article: {trainer_name} (Rank {rank})")
                
                # If no articles found on this page and we've gone through several pages, we might be at the end
                if not found_article and page > 10:
                    print("No more trainers with articles found")
                    break
                    
                # Check if we've reached the end (less than expected entries or no next page link)
                next_page = soup.select_one('a:-soup-contains("次へ")')
                if not next_page:
                    print("No next page link found")
                    break
                    
                page += 1
                time.sleep(random.uniform(1, 2))  # Be nice to the server
                
            except Exception as e:
                print(f"Error fetching trainer list page {page}: {str(e)}")
                break
        
        print(f"Found {len(trainers)} trainers with construction articles")
        return trainers

    def get_pokemon_details_from_article(self, article_url, pokemon_id):
        """Get Pokemon details from the construction article"""
        try:
            # Extract Pokemon number from ID
            pokemon_number = pokemon_id.split('-')[0]
            
            # Get the article page
            response = self.session.get(article_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find Pokemon data in the article
            # This is a simplified approach - articles may have different formats
            pokemon_data = {
                'name': '',
                'item': '',
                'ability': '',
                'nature': '',
                'tera_type': '',
                'moves': [],
                'evs': {'H': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'S': 0}
            }
            
            # Try to find the Pokemon name based on its number
            pokemon_sections = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'p'])
            
            # First, try to get the Pokemon name from the Pokedex
            pokemon_names = {
                # Gen 1
                "0001": "フシギダネ", "0002": "フシギソウ", "0003": "フシギバナ",
                "0004": "ヒトカゲ", "0005": "リザード", "0006": "リザードン",
                "0007": "ゼニガメ", "0008": "カメール", "0009": "カメックス",
                "0025": "ピカチュウ", "0026": "ライチュウ",
                "0059": "ウインディ",
                "0089": "ベトベトン", 
                "0110": "マタドガス",
                "0113": "ラッキー",
                "0131": "ラプラス",
                "0132": "メタモン",
                "0143": "カビゴン",
                "0149": "カイリュー",
                "0150": "ミュウツー",
                # Gen 2
                "0196": "エーフィ",
                "0211": "ハリーセン",
                "0212": "ハッサム",
                "0232": "ドンファン",
                "0235": "ツボツボ",
                "0242": "ハピナス",
                "0248": "バンギラス",
                "0249": "ルギア",
                "0250": "ホウオウ",
                # Gen 3
                "0260": "ラグラージ",
                "0282": "サーナイト",
                "0286": "キノガッサ",
                "0330": "フライゴン",
                "0380": "ラティアス",
                "0382": "カイオーガ",
                "0383": "グラードン",
                "0384": "レックウザ",
                # Gen 4
                "0426": "フワライド",
                "0437": "ドータクン",
                "0445": "ガブリアス",
                "0450": "カバルドン",
                "0472": "グライオン",
                "0479": "ロトム",
                "0485": "ヒードラン",
                "0487": "ギラティナ",
                "0488": "クレセリア",
                # Gen 5
                "0547": "フラージェス",
                "0594": "ママンボウ",
                # Gen 6
                "0645": "ランドロス",
                "0658": "ゲッコウガ",
                # Gen 7
                "0727": "オドリドリ",
                "0730": "アシレーヌ",
                "0745": "ルガルガン",
                "0748": "ドヒドイデ",
                "0778": "ミミッキュ",
                "0792": "ルナアーラ",
                # Gen 8
                "0800": "ネクロズマ",
                "0812": "ゴリランダー",
                "0823": "アーマーガア",
                "0855": "ヤバチャ",
                "0858": "ブリムオン",
                "0861": "グリムスナール",
                "0876": "イエッサン",
                "0877": "モルペコ",
                "0888": "ザシアン",
                "0889": "ザマゼンタ",
                "0890": "ムゲンダイナ",
                "0892": "ウーラオス",
                "0898": "バドレックス",
                # Gen 9
                "0901": "パオジアン",
                "0903": "ドオー",
                "0911": "ラウドボーン",
                "0923": "ブロロローム",
                "0925": "ラブトロス",
                "0934": "キョジオーン",
                "0970": "ハバタクカミ",
                "0973": "イダイナキバ",
                "0977": "ヘイラッシャ",
                "0978": "キチキギス",
                "0980": "テツノワダチ",
                "0981": "テツノカイナ",
                "0984": "デカヌチャン",
                "0986": "セグレイブ",
                "0987": "ディンルー",
                "0990": "イーユイ",
                "0991": "トドロクツキ",
                "0992": "テツノブジン",
                "1000": "ミライドン",
                "1001": "コライドン",
                "1002": "ウネルミナモ",
                "1003": "テツノドクガ",
                "1004": "サーフゴー",
                "1005": "チオンジェン",
                "1006": "パーモット",
                "1007": "オーガポン",
                "1008": "マシマシラ",
                "1009": "キラフロル",
                "1017": "オーロンゲ",
                "1018": "ブリジュラス",
                "1020": "ヒスイウォーグル",
                "1021": "ドドゲザン",
                "1024": "イイネイヌ",
            }
            
            # Get Pokemon name from the dictionary
            if pokemon_number in pokemon_names:
                pokemon_data['name'] = pokemon_names[pokemon_number]
            
            # Look for Pokemon data in the article
            for section in pokemon_sections:
                text = section.get_text(strip=True)
                
                # Skip empty sections
                if not text:
                    continue
                
                # Try to find the Pokemon name if not found yet
                if not pokemon_data['name'] and any(name in text for name in pokemon_names.values()):
                    for name in pokemon_names.values():
                        if name in text:
                            pokemon_data['name'] = name
                            break
                
                # Look for item
                item_patterns = [r'持ち物[：:]\s*([^\s]+)', r'もちもの[：:]\s*([^\s]+)', r'アイテム[：:]\s*([^\s]+)']
                for pattern in item_patterns:
                    item_match = re.search(pattern, text)
                    if item_match and not pokemon_data['item']:
                        pokemon_data['item'] = item_match.group(1)
                
                # Look for ability
                ability_patterns = [r'特性[：:]\s*([^\s]+)', r'とくせい[：:]\s*([^\s]+)']
                for pattern in ability_patterns:
                    ability_match = re.search(pattern, text)
                    if ability_match and not pokemon_data['ability']:
                        pokemon_data['ability'] = ability_match.group(1)
                
                # Look for nature
                nature_patterns = [r'性格[：:]\s*([^\s]+)', r'せいかく[：:]\s*([^\s]+)']
                for pattern in nature_patterns:
                    nature_match = re.search(pattern, text)
                    if nature_match and not pokemon_data['nature']:
                        pokemon_data['nature'] = nature_match.group(1)
                
                # Look for Tera type
                tera_patterns = [r'テラスタイプ[：:]\s*([^\s]+)', r'テラス[：:]\s*([^\s]+)', r'テラ[：:]\s*([^\s]+)']
                for pattern in tera_patterns:
                    tera_match = re.search(pattern, text)
                    if tera_match and not pokemon_data['tera_type']:
                        pokemon_data['tera_type'] = tera_match.group(1)
                
                # Look for moves
                move_patterns = [r'技[：:]\s*([^、]+)、([^、]+)、([^、]+)、([^、]+)', 
                                r'わざ[：:]\s*([^、]+)、([^、]+)、([^、]+)、([^、]+)',
                                r'技構成[：:]\s*([^、]+)、([^、]+)、([^、]+)、([^、]+)']
                for pattern in move_patterns:
                    move_match = re.search(pattern, text)
                    if move_match and not pokemon_data['moves']:
                        pokemon_data['moves'] = [move_match.group(1), move_match.group(2), 
                                                move_match.group(3), move_match.group(4)]
                
                # Look for EVs
                ev_patterns = [
                    r'努力値[：:]\s*(?:H|HP)(\d+)\s*(?:A|攻撃)(\d+)\s*(?:B|防御)(\d+)\s*(?:C|特攻)(\d+)\s*(?:D|特防)(\d+)\s*(?:S|素早)(\d+)',
                    r'努力値[：:]\s*(?:HP|H)(\d+)\s*(?:攻撃|A)(\d+)\s*(?:防御|B)(\d+)\s*(?:特攻|C)(\d+)\s*(?:特防|D)(\d+)\s*(?:素早さ|S)(\d+)'
                ]
                for pattern in ev_patterns:
                    ev_match = re.search(pattern, text)
                    if ev_match and all(v == 0 for v in pokemon_data['evs'].values()):
                        pokemon_data['evs'] = {
                            'H': int(ev_match.group(1)),
                            'A': int(ev_match.group(2)),
                            'B': int(ev_match.group(3)),
                            'C': int(ev_match.group(4)),
                            'D': int(ev_match.group(5)),
                            'S': int(ev_match.group(6))
                        }
            
            # If we found at least the name, return the data
            if pokemon_data['name']:
                return pokemon_data
            
            # If we couldn't find the data in the article, use default values
            return {
                'name': pokemon_names.get(pokemon_number, f"ポケモン{pokemon_number}"),
                'item': '不明',
                'ability': '不明',
                'nature': '不明',
                'tera_type': '不明',
                'moves': ['不明'] * 4,
                'evs': {'H': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0, 'S': 0}
            }
            
        except Exception as e:
            print(f"Error fetching Pokemon details from article for {pokemon_id}: {str(e)}")
            return None

    def scrape_article_trainers(self, season=27, rule=0, party=1, max_trainers=None):
        """Scrape trainer and Pokemon data for trainers with construction articles"""
        print(f"Fetching trainers with construction articles for Season {season}...")
        trainers = self.get_trainers_with_articles(season, rule, party)
        
        if max_trainers:
            trainers = trainers[:max_trainers]
        
        trainer_data = []
        total = len(trainers)
        
        for i, trainer in enumerate(trainers, 1):
            print(f"Processing trainer {i}/{total}: {trainer['trainer_name']} (Rank {trainer['rank']})")
            
            pokemon_list = []
            for pokemon_id in trainer['pokemon_ids']:
                print(f"  Fetching details for Pokemon ID: {pokemon_id}")
                # Try to get Pokemon details from the article
                pokemon_data = self.get_pokemon_details_from_article(trainer['article_url'], pokemon_id)
                
                if pokemon_data:
                    pokemon_list.append(pokemon_data)
                    print(f"  Added {pokemon_data['name']}")
                else:
                    print(f"  Failed to get data for Pokemon ID: {pokemon_id}")
                
                time.sleep(random.uniform(0.5, 1))  # Be nice to the server
            
            trainer_data.append({
                'rank': trainer['rank'],
                'rating': trainer['rating'],
                'trainer_name': trainer['trainer_name'],
                'article_url': trainer.get('article_url', ''),
                'pokemon': pokemon_list
            })
            
            # Save progress periodically
            if i % 5 == 0 or i == total:
                print(f"Saving progress after processing {i}/{total} trainers...")
                with open('trainer_data.json', 'w', encoding='utf-8') as f:
                    json.dump(trainer_data, f, ensure_ascii=False, indent=2)
        
        # Save final results
        with open('trainer_data.json', 'w', encoding='utf-8') as f:
            json.dump(trainer_data, f, ensure_ascii=False, indent=2)
        
        print(f"Completed scraping {len(trainer_data)} trainers with construction articles")
        return trainer_data

if __name__ == "__main__":
    scraper = PokemonSVScraper()
    # Scrape trainers with construction articles from Season 27
    scraper.scrape_article_trainers(season=27, rule=0, party=1)