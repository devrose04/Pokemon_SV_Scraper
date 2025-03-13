# Pokémon SV Trainer Data Scraper / ポケモンSVトレーナーデータスクレイパー

This project scrapes trainer data from the sv.pokedb.tokyo website and external blog links to collect information about top-ranked Pokémon SV trainers and their teams.

このプロジェクトは、sv.pokedb.tokyoウェブサイトと外部ブログリンクからトレーナーデータをスクレイピングし、ポケモンSVのトップランクトレーナーとそのチームに関する情報を収集します。

## Project Requirements / プロジェクト要件

以下のデータ収集作業を行います：

1. **データソース**：
   - https://sv.pokedb.tokyo/trainer/list?season=27&rule=0&party=1 より、シーズン27で公開されている構築記事からデータを収集

2. **収集するデータ**：
   - トレーナー名
   - 順位
   - レート
   - ポケモン6匹についてそれぞれ：
     - ポケモン名
     - 特性
     - アイテム
     - テラスタルタイプ
     - 性格
     - 技一覧
     - 努力値一覧（HP、攻撃、防御、特攻、特防、素早さ）

3. **作業量**：
   - 約150記事
   - 1記事あたり5〜10分程度の作業時間

4. **出力先**：
   - 指定されたGoogleスプレッドシート
   - スプレッドシートには入力例が記載されています

## Features / 機能

- Scrapes trainer data from external blog links / 外部ブログリンクからトレーナーデータをスクレイピング
- Extracts Pokémon team information from blog posts / ブログ投稿からポケモンチーム情報を抽出
- Saves data in a structured JSON format / 構造化されたJSON形式でデータを保存
- Uploads data to Google Sheets (optional) / Google Sheetsにデータをアップロード（オプション）

## Requirements / 必要条件

- Python 3.6+
- requests
- BeautifulSoup4
- gspread (for Google Sheets integration / Google Sheets連携用)
- oauth2client (for Google Sheets integration / Google Sheets連携用)

## Installation / インストール

1. Clone this repository / このリポジトリをクローン
2. Create a virtual environment / 仮想環境を作成:
   ```
   python -m venv .venv
   ```
3. Activate the virtual environment / 仮想環境を有効化:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
4. Install dependencies / 依存関係をインストール:
   ```
   pip install -r requirements.txt
   ```

## Usage / 使用方法

### Basic Usage / 基本的な使用方法

Run the main script / メインスクリプトを実行:

```
python main.py
```

This will / これにより:
1. Fetch the trainer list from sv.pokedb.tokyo / sv.pokedb.tokyoからトレーナーリストを取得
2. Extract blog links from the table / テーブルからブログリンクを抽出
3. Visit each blog and extract Pokémon team information / 各ブログを訪問してポケモンチーム情報を抽出
4. Save the data to `trainer_data.json` / データを`trainer_data.json`に保存

### GUI Application / GUIアプリケーション

Run the GUI application / GUIアプリケーションを実行:

```
python gui_app.py
```

Or use the batch file / またはバッチファイルを使用:

```
run_gui.bat
```

### Advanced Usage / 高度な使用方法

The script supports several command-line arguments / スクリプトはいくつかのコマンドライン引数をサポートしています:

```
python main.py --limit 20 --delay 2 --output custom_output.json
```

Available options / 利用可能なオプション:
- `--limit N`: Limit the number of trainers to scrape (default: 10, use 0 for all) / スクレイピングするトレーナーの数を制限（デフォルト：10、すべての場合は0を使用）
- `--delay N`: Set the delay between requests in seconds (default: 1.0) / リクエスト間の遅延を秒単位で設定（デフォルト：1.0）
- `--output FILE`: Specify the output JSON file (default: trainer_data.json) / 出力JSONファイルを指定（デフォルト：trainer_data.json）
- `--upload`: Upload data to Google Sheets / Google Sheetsにデータをアップロード
- `--spreadsheet NAME`: Specify the name of the Google Spreadsheet (default: "Pokemon SV Trainer Data") / Google Spreadsheetの名前を指定（デフォルト："Pokemon SV Trainer Data"）
- `--credentials FILE`: Specify the path to the Google API credentials file (default: credentials.json) / Google API認証情報ファイルへのパスを指定（デフォルト：credentials.json）

### Google Sheets Integration / Google Sheets連携

To upload data to Google Sheets / Google Sheetsにデータをアップロードするには:

1. Set up a Google Cloud project and enable the Google Sheets API / Google Cloudプロジェクトを設定し、Google Sheets APIを有効にする
2. Create a service account and download the credentials JSON file / サービスアカウントを作成し、認証情報JSONファイルをダウンロード
3. Use the `create_credentials.py` script to set up your credentials / `create_credentials.py`スクリプトを使用して認証情報を設定:
   ```
   python create_credentials.py
   ```
4. Run the script with the `--upload` flag / `--upload`フラグを付けてスクリプトを実行:
   ```
   python main.py --upload
   ```

#### Setting up Google Cloud Credentials / Google Cloud認証情報の設定

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) / [Google Cloudコンソール](https://console.cloud.google.com/)にアクセス
2. Create a new project / 新しいプロジェクトを作成
3. Enable the Google Sheets API and Google Drive API / Google Sheets APIとGoogle Drive APIを有効にする
4. Create a service account / サービスアカウントを作成
5. Download the JSON key file / JSONキーファイルをダウンロード
6. Use the `create_credentials.py` script to set up your credentials / `create_credentials.py`スクリプトを使用して認証情報を設定
7. Share your Google Spreadsheet with the service account email address / サービスアカウントのメールアドレスとGoogle Spreadsheetを共有

#### Testing Google Sheets Integration / Google Sheets連携のテスト

You can test your Google Sheets integration with the `test_sheets.py` script / `test_sheets.py`スクリプトでGoogle Sheets連携をテストできます:

```
python test_sheets.py
```

This script will check if your credentials are valid and try to upload the data to a test spreadsheet / このスクリプトは認証情報が有効かどうかを確認し、テストスプレッドシートにデータをアップロードしようとします。

## Output Format / 出力形式

The output is a JSON file with the following structure / 出力は以下の構造のJSONファイルです:

```json
[
  {
    "trainer_name": "トレーナー名",
    "rank": "順位",
    "rating": "レート",
    "pokemon": [
      {
        "name": "ポケモン名",
        "ability": "特性",
        "item": "持ち物",
        "tera_type": "テラスタイプ",
        "nature": "性格",
        "moves": ["技1", "技2", "技3", "技4"],
        "evs": {
          "H": "HP努力値",
          "A": "攻撃努力値",
          "B": "防御努力値",
          "C": "特攻努力値",
          "D": "特防努力値",
          "S": "素早さ努力値"
        }
      },
      // More Pokémon...
    ],
    "url": "ブログURL"
  },
  // More trainers...
]
```

## Google Sheets Format / Google Sheets形式

When uploading to Google Sheets, the data is organized into two worksheets / Google Sheetsにアップロードする際、データは2つのワークシートに整理されます:

1. **Trainer Data / トレーナーデータ**: Contains basic information about each trainer / 各トレーナーの基本情報を含む
   - Trainer Name / トレーナー名
   - Rank / 順位
   - Rating / レート
   - URL / URL
   - Pokémon Count / ポケモン数
   - Pokémon Names (comma-separated) / ポケモン名（カンマ区切り）

2. **Pokemon Details / ポケモン詳細**: Contains detailed information about each Pokémon / 各ポケモンの詳細情報を含む
   - Trainer Name / トレーナー名
   - Pokémon Name / ポケモン名
   - Ability / 特性
   - Item / 持ち物
   - Tera Type / テラスタイプ
   - Nature / 性格
   - Moves / 技
   - EVs (HP, Atk, Def, SpA, SpD, Spe) / 努力値（HP、攻撃、防御、特攻、特防、素早さ）

## Limitations / 制限事項

- The current implementation only extracts Pokémon names from blog posts / 現在の実装ではブログ投稿からポケモン名のみを抽出
- Detailed information like abilities, items, moves, etc. are marked as "不明" (unknown) / 特性、持ち物、技などの詳細情報は「不明」としてマーク
- The script relies on a predefined list of common Pokémon names in Japanese / スクリプトは日本語の一般的なポケモン名の事前定義リストに依存

## Future Improvements / 今後の改善点

- Implement more sophisticated parsing to extract detailed Pokémon information / より詳細なポケモン情報を抽出するための高度な解析を実装
- Add support for different blog formats / 異なるブログ形式のサポートを追加
- Implement pagination to scrape more than just the first page of trainers / 最初のページだけでなく、複数ページのトレーナーをスクレイピングするためのページネーションを実装
- Add error handling and retry mechanisms for failed requests / 失敗したリクエストのためのエラー処理と再試行メカニズムを追加 