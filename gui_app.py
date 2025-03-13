import os
import sys
import json
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# Import the main functionality if available
try:
    from main import get_trainer_urls, parse_trainer_page
    MAIN_AVAILABLE = True
except ImportError:
    MAIN_AVAILABLE = False

# Import the sheets uploader if available
try:
    from sheets_uploader import upload_to_sheets
    SHEETS_AVAILABLE = True
except ImportError:
    SHEETS_AVAILABLE = False

class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = StringIO()

    def write(self, string):
        self.buffer.write(string)
        self.text_widget.configure(state="normal")
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state="disabled")

    def flush(self):
        pass

class PokemonScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokémon SV Trainer Data Scraper / ポケモンSVトレーナーデータスクレイパー")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Set icon if available
        try:
            self.root.iconbitmap("pokemon_icon.ico")
        except:
            pass
        
        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.scraper_tab = ttk.Frame(self.notebook)
        self.sheets_tab = ttk.Frame(self.notebook)
        self.about_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.scraper_tab, text="Scraper / スクレイパー")
        self.notebook.add(self.sheets_tab, text="Google Sheets")
        self.notebook.add(self.about_tab, text="About / 概要")
        
        # Setup each tab
        self.setup_scraper_tab()
        self.setup_sheets_tab()
        self.setup_about_tab()
        
        # Flag to track if scraping is running
        self.scraping_running = False
        self.scraping_thread = None
        
        # Flag to track if upload is running
        self.upload_running = False
        self.upload_thread = None
        
        # Print welcome message
        sys.stdout = self.stdout_redirect
        print("Welcome to the Pokémon SV Trainer Data Scraper!")
        print("ポケモンSVトレーナーデータスクレイパーへようこそ！")
        print("Select options and click 'Start Scraping' to begin.")
        print("オプションを選択し、「スクレイピング開始」をクリックして開始してください。")
        sys.stdout = sys.__stdout__

    def setup_scraper_tab(self):
        # Create a frame for the options
        options_frame = ttk.LabelFrame(self.scraper_tab, text="Scraping Options / スクレイピングオプション")
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # URL input
        ttk.Label(options_frame, text="Base URL / 基本URL:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.url_var = tk.StringVar(value="https://sv.pokedb.tokyo/trainer/list?season=27&rule=0&party=1")
        ttk.Entry(options_frame, textvariable=self.url_var, width=50).grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Limit input
        ttk.Label(options_frame, text="Limit (0 for all) / 制限 (0ですべて):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.limit_var = tk.IntVar(value=10)
        ttk.Spinbox(options_frame, from_=0, to=1000, textvariable=self.limit_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Delay input
        ttk.Label(options_frame, text="Delay (seconds) / 遅延 (秒):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.delay_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(options_frame, from_=0.1, to=10.0, increment=0.1, textvariable=self.delay_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Output file input
        ttk.Label(options_frame, text="Output file / 出力ファイル:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        output_frame = ttk.Frame(options_frame)
        output_frame.grid(row=3, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        self.output_var = tk.StringVar(value="trainer_data.json")
        ttk.Entry(output_frame, textvariable=self.output_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Browse... / 参照...", command=self.browse_output).pack(side=tk.RIGHT, padx=5)
        
        # Create a frame for the buttons
        button_frame = ttk.Frame(self.scraper_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Start button
        self.start_button = ttk.Button(button_frame, text="Start Scraping / スクレイピング開始", command=self.start_scraping)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Stop button
        self.stop_button = ttk.Button(button_frame, text="Stop / 停止", command=self.stop_scraping, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # View results button
        self.view_button = ttk.Button(button_frame, text="View Results / 結果を表示", command=self.view_results)
        self.view_button.pack(side=tk.LEFT, padx=5)
        
        # Create a frame for the log
        log_frame = ttk.LabelFrame(self.scraper_tab, text="Log / ログ")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Log text widget
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Redirect stdout and stderr to the log text widget
        self.stdout_redirect = RedirectText(self.log_text)
    
    def setup_sheets_tab(self):
        # Create a frame for the options
        options_frame = ttk.LabelFrame(self.sheets_tab, text="Google Sheets Options / Google Sheetsオプション")
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Spreadsheet name input
        ttk.Label(options_frame, text="Spreadsheet name / スプレッドシート名:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.spreadsheet_var = tk.StringVar(value="Pokemon SV Trainer Data")
        ttk.Entry(options_frame, textvariable=self.spreadsheet_var, width=40).grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Credentials file input
        ttk.Label(options_frame, text="Credentials file / 認証情報ファイル:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        creds_frame = ttk.Frame(options_frame)
        creds_frame.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        self.credentials_var = tk.StringVar(value="credentials.json")
        ttk.Entry(creds_frame, textvariable=self.credentials_var, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(creds_frame, text="Browse... / 参照...", command=self.browse_credentials).pack(side=tk.LEFT, padx=5)
        ttk.Button(creds_frame, text="Setup / 設定", command=self.setup_credentials).pack(side=tk.LEFT)
        
        # JSON file input
        ttk.Label(options_frame, text="JSON data file / JSONデータファイル:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        json_frame = ttk.Frame(options_frame)
        json_frame.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        self.json_var = tk.StringVar(value="trainer_data.json")
        ttk.Entry(json_frame, textvariable=self.json_var, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(json_frame, text="Browse... / 参照...", command=self.browse_json).pack(side=tk.LEFT, padx=5)
        
        # Create a frame for the buttons
        button_frame = ttk.Frame(self.sheets_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Upload button
        self.upload_button = ttk.Button(button_frame, text="Upload to Google Sheets / Google Sheetsにアップロード", command=self.upload_to_sheets)
        self.upload_button.pack(side=tk.LEFT, padx=5)
        
        # Test connection button
        self.test_button = ttk.Button(button_frame, text="Test Connection / 接続テスト", command=self.test_connection)
        self.test_button.pack(side=tk.LEFT, padx=5)
        
        # Create a frame for the log
        log_frame = ttk.LabelFrame(self.sheets_tab, text="Log / ログ")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Log text widget
        self.sheets_log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.sheets_log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_about_tab(self):
        # Create a frame for the about information
        about_frame = ttk.Frame(self.about_tab)
        about_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(about_frame, text="Pokémon SV Trainer Data Scraper / ポケモンSVトレーナーデータスクレイパー", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        # Description
        description = """
This application scrapes trainer data from the sv.pokedb.tokyo website and external blog links
to collect information about top-ranked Pokémon SV trainers and their teams.

このアプリケーションは、sv.pokedb.tokyoウェブサイトと外部ブログリンクからトレーナーデータをスクレイピングし、
ポケモンSVのトップランクトレーナーとそのチームに関する情報を収集します。

Features / 機能:
- Scrapes trainer data from external blog links / 外部ブログリンクからトレーナーデータをスクレイピング
- Extracts Pokémon team information from blog posts / ブログ投稿からポケモンチーム情報を抽出
- Saves data in a structured JSON format / 構造化されたJSON形式でデータを保存
- Uploads data to Google Sheets (optional) / Google Sheetsにデータをアップロード（オプション）

Version / バージョン: 1.0.0
        """
        
        desc_label = ttk.Label(about_frame, text=description, justify=tk.LEFT, wraplength=700)
        desc_label.pack(pady=10, fill=tk.X)
        
        # GitHub link
        github_frame = ttk.Frame(about_frame)
        github_frame.pack(pady=10)
        
        ttk.Label(github_frame, text="GitHub Repository / GitHubリポジトリ:").pack(side=tk.LEFT)
        github_link = ttk.Label(github_frame, text="https://github.com/yourusername/pokemon-sv-scraper", foreground="blue", cursor="hand2")
        github_link.pack(side=tk.LEFT, padx=5)
        github_link.bind("<Button-1>", lambda e: self.open_url("https://github.com/yourusername/pokemon-sv-scraper"))
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=self.output_var.get()
        )
        if filename:
            self.output_var.set(filename)
    
    def browse_credentials(self):
        filename = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=self.credentials_var.get()
        )
        if filename:
            self.credentials_var.set(filename)
    
    def browse_json(self):
        filename = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=self.json_var.get()
        )
        if filename:
            self.json_var.set(filename)
    
    def setup_credentials(self):
        # Run the create_credentials.py script in a separate window
        try:
            if sys.platform == 'win32':
                subprocess.Popen(["start", "cmd", "/k", f"{sys.executable}", "create_credentials.py"], shell=True)
            else:
                subprocess.Popen([sys.executable, "create_credentials.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run create_credentials.py: {str(e)}")
    
    def start_scraping(self):
        # Disable the start button and enable the stop button
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Clear the log
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state=tk.DISABLED)
        
        # Start the scraping thread
        self.scraping_thread = threading.Thread(target=self.scrape_data)
        self.scraping_thread.daemon = True
        self.scraping_thread.start()
    
    def scrape_data(self):
        # Redirect stdout and stderr to the log text widget
        with redirect_stdout(self.stdout_redirect), redirect_stderr(self.stdout_redirect):
            try:
                # Get the options
                base_url = self.url_var.get()
                limit = self.limit_var.get()
                delay = self.delay_var.get()
                output_file = self.output_var.get()
                
                print(f"Starting scraping with the following options:")
                print(f"Base URL: {base_url}")
                print(f"Limit: {limit}")
                print(f"Delay: {delay} seconds")
                print(f"Output file: {output_file}")
                print()
                
                # Run the scraping process
                if MAIN_AVAILABLE:
                    import time
                    from main import get_trainer_urls, parse_trainer_page
                    
                    # Get trainer URLs
                    print("Getting trainer URLs...")
                    trainer_urls = get_trainer_urls(base_url)
                    print(f"Found {len(trainer_urls)} trainer URLs")
                    
                    # Limit the number of trainers if specified
                    if limit > 0:
                        trainer_urls = trainer_urls[:limit]
                        print(f"Limited to {limit} trainers")
                    
                    # Parse each trainer page
                    all_trainer_data = []
                    for i, url in enumerate(trainer_urls):
                        if hasattr(self, 'stop_requested') and self.stop_requested:
                            print("Scraping stopped by user.")
                            break
                        
                        print(f"Parsing trainer {i+1}/{len(trainer_urls)}: {url}")
                        trainer_data = parse_trainer_page(url)
                        all_trainer_data.append(trainer_data)
                        
                        # Add a delay to avoid overloading the server
                        if i < len(trainer_urls) - 1:  # No need to delay after the last request
                            time.sleep(delay)
                    
                    # Save the data to a JSON file
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(all_trainer_data, f, ensure_ascii=False, indent=2)
                    
                    print(f"Successfully scraped {len(all_trainer_data)} trainer pages")
                    print(f"Data saved to {output_file}")
                else:
                    # Run the main.py script as a subprocess
                    cmd = [
                        sys.executable, "main.py",
                        "--limit", str(limit),
                        "--delay", str(delay),
                        "--output", output_file
                    ]
                    
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )
                    
                    # Read the output line by line
                    for line in process.stdout:
                        print(line, end='')
                        
                        # Check if the user requested to stop
                        if hasattr(self, 'stop_requested') and self.stop_requested:
                            process.terminate()
                            print("Scraping stopped by user.")
                            break
                    
                    process.wait()
                    
                    if process.returncode != 0 and not (hasattr(self, 'stop_requested') and self.stop_requested):
                        print(f"Error: The scraping process exited with code {process.returncode}")
                    elif not (hasattr(self, 'stop_requested') and self.stop_requested):
                        print("Scraping completed successfully.")
            
            except Exception as e:
                print(f"Error: {str(e)}")
            
            finally:
                # Re-enable the start button and disable the stop button
                self.root.after(0, self.reset_buttons)
    
    def reset_buttons(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if hasattr(self, 'stop_requested'):
            delattr(self, 'stop_requested')
    
    def stop_scraping(self):
        self.stop_requested = True
        self.stop_button.config(state=tk.DISABLED)
        print("Stopping scraping... Please wait.")
    
    def view_results(self):
        output_file = self.output_var.get()
        if not os.path.exists(output_file):
            messagebox.showerror("Error", f"The file {output_file} does not exist.")
            return
        
        try:
            # Open the file with the default application
            if sys.platform == 'win32':
                os.startfile(output_file)
            elif sys.platform == 'darwin':  # macOS
                subprocess.call(['open', output_file])
            else:  # Linux
                subprocess.call(['xdg-open', output_file])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open the file: {str(e)}")
    
    def upload_to_sheets(self):
        # Disable the upload button
        self.upload_button.config(state=tk.DISABLED)
        
        # Clear the log
        self.sheets_log_text.configure(state=tk.NORMAL)
        self.sheets_log_text.delete(1.0, tk.END)
        self.sheets_log_text.configure(state=tk.DISABLED)
        
        # Start the uploading thread
        self.upload_thread = threading.Thread(target=self.upload_data)
        self.upload_thread.daemon = True
        self.upload_thread.start()
    
    def upload_data(self):
        # Redirect stdout and stderr to the sheets log text widget
        stdout_redirect = RedirectText(self.sheets_log_text)
        
        with redirect_stdout(stdout_redirect), redirect_stderr(stdout_redirect):
            try:
                # Get the options
                spreadsheet_name = self.spreadsheet_var.get()
                credentials_file = self.credentials_var.get()
                json_file = self.json_var.get()
                
                print(f"Uploading data to Google Sheets with the following options:")
                print(f"Spreadsheet name: {spreadsheet_name}")
                print(f"Credentials file: {credentials_file}")
                print(f"JSON data file: {json_file}")
                print()
                
                # Check if the files exist
                if not os.path.exists(credentials_file):
                    print(f"Error: The credentials file {credentials_file} does not exist.")
                    print("Please set up your credentials first.")
                    return
                
                if not os.path.exists(json_file):
                    print(f"Error: The JSON data file {json_file} does not exist.")
                    print("Please run the scraper first to generate the data.")
                    return
                
                # Upload the data to Google Sheets
                if SHEETS_AVAILABLE:
                    from sheets_uploader import upload_to_sheets
                    upload_to_sheets(json_file, spreadsheet_name, credentials_file)
                else:
                    # Run the sheets_uploader.py script as a subprocess
                    cmd = [
                        sys.executable, "-c",
                        "from sheets_uploader import upload_to_sheets; "
                        f"upload_to_sheets('{json_file}', '{spreadsheet_name}', '{credentials_file}')"
                    ]
                    
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )
                    
                    # Read the output line by line
                    for line in process.stdout:
                        print(line, end='')
                    
                    process.wait()
                    
                    if process.returncode != 0:
                        print(f"Error: The upload process exited with code {process.returncode}")
                    else:
                        print("Upload completed successfully.")
            
            except Exception as e:
                print(f"Error: {str(e)}")
            
            finally:
                # Re-enable the upload button
                self.root.after(0, lambda: self.upload_button.config(state=tk.NORMAL))
    
    def test_connection(self):
        # Clear the log
        self.sheets_log_text.configure(state=tk.NORMAL)
        self.sheets_log_text.delete(1.0, tk.END)
        self.sheets_log_text.configure(state=tk.DISABLED)
        
        # Redirect stdout and stderr to the sheets log text widget
        stdout_redirect = RedirectText(self.sheets_log_text)
        
        with redirect_stdout(stdout_redirect), redirect_stderr(stdout_redirect):
            try:
                # Get the credentials file
                credentials_file = self.credentials_var.get()
                
                print(f"Testing connection to Google Sheets API with credentials file: {credentials_file}")
                print()
                
                # Check if the file exists
                if not os.path.exists(credentials_file):
                    print(f"Error: The credentials file {credentials_file} does not exist.")
                    print("Please set up your credentials first.")
                    return
                
                # Test the connection
                if SHEETS_AVAILABLE:
                    import gspread
                    from oauth2client.service_account import ServiceAccountCredentials
                    
                    # Set up the credentials for the Google Sheets API
                    scope = ['https://spreadsheets.google.com/feeds',
                             'https://www.googleapis.com/auth/drive']
                    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
                    client = gspread.authorize(credentials)
                    
                    # Try to create a test spreadsheet
                    test_spreadsheet = client.create("Test Connection")
                    print(f"Successfully connected to Google Sheets API!")
                    print(f"Created test spreadsheet: Test Connection")
                    print(f"Spreadsheet URL: https://docs.google.com/spreadsheets/d/{test_spreadsheet.id}")
                    
                    # Delete the test spreadsheet
                    client.del_spreadsheet(test_spreadsheet.id)
                    print("Test spreadsheet deleted.")
                else:
                    # Run the test_sheets.py script as a subprocess
                    cmd = [sys.executable, "test_sheets.py"]
                    
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        universal_newlines=True
                    )
                    
                    # Read the output line by line
                    for line in process.stdout:
                        print(line, end='')
                    
                    process.wait()
                    
                    if process.returncode != 0:
                        print(f"Error: The test process exited with code {process.returncode}")
                    else:
                        print("Connection test completed successfully.")
            
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def open_url(self, url):
        import webbrowser
        webbrowser.open_new(url)

def main():
    root = tk.Tk()
    app = PokemonScraperApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 