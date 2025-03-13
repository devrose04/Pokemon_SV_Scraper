import os
import sys
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from sheets_uploader import upload_to_sheets, get_resource_path
from pokemon_scraper import PokemonSVScraper

class PokemonSVUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokemon SV Uploader")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Set icon if available
        icon_path = get_resource_path("pokemon_icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.tab_control = ttk.Notebook(main_frame)
        
        # Scraper tab
        self.scraper_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.scraper_tab, text="Scraper")
        
        # Uploader tab
        self.uploader_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.uploader_tab, text="Uploader")
        
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Setup tabs
        self._setup_scraper_tab()
        self._setup_uploader_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _setup_scraper_tab(self):
        # Create frame with padding
        frame = ttk.Frame(self.scraper_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(frame, text="Pokemon SV Scraper", font=("Helvetica", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)
        
        # Season selection
        ttk.Label(frame, text="Season:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.season_var = tk.IntVar(value=27)
        season_entry = ttk.Spinbox(frame, from_=1, to=100, textvariable=self.season_var, width=10)
        season_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Rule selection
        ttk.Label(frame, text="Rule:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.rule_var = tk.IntVar(value=0)
        rule_combo = ttk.Combobox(frame, textvariable=self.rule_var, width=20)
        rule_combo['values'] = (0, 1, 2)
        rule_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Party selection
        ttk.Label(frame, text="Party:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.party_var = tk.IntVar(value=1)
        party_combo = ttk.Combobox(frame, textvariable=self.party_var, width=20)
        party_combo['values'] = (1, 2)
        party_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Max trainers
        ttk.Label(frame, text="Max Trainers:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.max_trainers_var = tk.IntVar(value=50)
        max_trainers_entry = ttk.Spinbox(frame, from_=1, to=1000, textvariable=self.max_trainers_var, width=10)
        max_trainers_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Output file
        ttk.Label(frame, text="Output File:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.output_file_var = tk.StringVar(value="trainer_data.json")
        output_entry = ttk.Entry(frame, textvariable=self.output_file_var, width=30)
        output_entry.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Progress
        ttk.Label(frame, text="Progress:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Log frame
        log_frame = ttk.LabelFrame(frame, text="Log")
        log_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Log text
        self.log_text = tk.Text(log_frame, height=10, width=60, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for log
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        # Start button
        self.start_button = ttk.Button(button_frame, text="Start Scraping", command=self.start_scraping)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(7, weight=1)
    
    def _setup_uploader_tab(self):
        # Create frame with padding
        frame = ttk.Frame(self.uploader_tab, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(frame, text="Pokemon SV Uploader", font=("Helvetica", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky=tk.W)
        
        # JSON file selection
        ttk.Label(frame, text="JSON Data File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.json_file_var = tk.StringVar(value="trainer_data.json")
        json_entry = ttk.Entry(frame, textvariable=self.json_file_var, width=40)
        json_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        browse_json_btn = ttk.Button(frame, text="Browse", command=self.browse_json)
        browse_json_btn.grid(row=1, column=2, padx=5, pady=5)
        
        # Credentials file selection
        ttk.Label(frame, text="Credentials File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.credentials_file_var = tk.StringVar(value="credentials.json")
        cred_entry = ttk.Entry(frame, textvariable=self.credentials_file_var, width=40)
        cred_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        browse_cred_btn = ttk.Button(frame, text="Browse", command=self.browse_credentials)
        browse_cred_btn.grid(row=2, column=2, padx=5, pady=5)
        
        # Spreadsheet name
        ttk.Label(frame, text="Spreadsheet Name:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.spreadsheet_name_var = tk.StringVar(value="Pokemon SV Trainer Data")
        name_entry = ttk.Entry(frame, textvariable=self.spreadsheet_name_var, width=40)
        name_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Spreadsheet ID
        ttk.Label(frame, text="Spreadsheet ID:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.spreadsheet_id_var = tk.StringVar(value="1wiBHSCdacFaPJoYV17C1OzLe-MitprC8dtrb7hh4wZY")
        id_entry = ttk.Entry(frame, textvariable=self.spreadsheet_id_var, width=40)
        id_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Data preview frame
        preview_frame = ttk.LabelFrame(frame, text="Data Preview")
        preview_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Data preview text
        self.preview_text = tk.Text(preview_frame, height=10, width=60, wrap=tk.WORD)
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for preview
        scrollbar = ttk.Scrollbar(preview_frame, command=self.preview_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_text.config(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        # Preview button
        preview_button = ttk.Button(button_frame, text="Preview Data", command=self.preview_data)
        preview_button.pack(side=tk.LEFT, padx=5)
        
        # Upload button
        upload_button = ttk.Button(button_frame, text="Upload to Sheets", command=self.upload_data)
        upload_button.pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(5, weight=1)
    
    def log(self, message):
        """Add message to log text widget"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def browse_json(self):
        """Browse for JSON data file"""
        filename = filedialog.askopenfilename(
            title="Select JSON Data File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.json_file_var.set(filename)
    
    def browse_credentials(self):
        """Browse for credentials file"""
        filename = filedialog.askopenfilename(
            title="Select Credentials File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.credentials_file_var.set(filename)
    
    def preview_data(self):
        """Preview the JSON data"""
        json_file = self.json_file_var.get()
        
        if not os.path.exists(json_file):
            messagebox.showerror("Error", f"File not found: {json_file}")
            return
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.preview_text.delete(1.0, tk.END)
            
            if not data:
                self.preview_text.insert(tk.END, "No data found in the file.")
                return
            
            self.preview_text.insert(tk.END, f"Found {len(data)} trainers\n\n")
            
            # Show first 2 trainers as preview
            for i, trainer in enumerate(data[:2]):
                self.preview_text.insert(tk.END, f"Trainer {i+1}: {trainer.get('trainer_name', 'Unknown')}\n")
                self.preview_text.insert(tk.END, f"Rank: {trainer.get('rank', 'Unknown')}\n")
                self.preview_text.insert(tk.END, f"Rating: {trainer.get('rating', 'Unknown')}\n")
                
                pokemon_list = trainer.get('pokemon', [])
                self.preview_text.insert(tk.END, f"Pokemon: {len(pokemon_list)}\n")
                
                for j, pokemon in enumerate(pokemon_list[:2]):  # Show first 2 Pokemon
                    self.preview_text.insert(tk.END, f"  {j+1}. {pokemon.get('name', 'Unknown')}\n")
                
                if len(pokemon_list) > 2:
                    self.preview_text.insert(tk.END, f"  ... and {len(pokemon_list) - 2} more\n")
                
                self.preview_text.insert(tk.END, "\n")
            
            if len(data) > 2:
                self.preview_text.insert(tk.END, f"... and {len(data) - 2} more trainers")
            
        except Exception as e:
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"Error loading data: {str(e)}")
    
    def upload_data(self):
        """Upload data to Google Sheets"""
        json_file = self.json_file_var.get()
        credentials_file = self.credentials_file_var.get()
        spreadsheet_name = self.spreadsheet_name_var.get()
        spreadsheet_id = self.spreadsheet_id_var.get()
        
        if not os.path.exists(json_file):
            messagebox.showerror("Error", f"JSON file not found: {json_file}")
            return
        
        if not os.path.exists(credentials_file):
            messagebox.showerror("Error", f"Credentials file not found: {credentials_file}")
            return
        
        if not spreadsheet_id:
            messagebox.showerror("Error", "Spreadsheet ID is required")
            return
        
        self.status_var.set("Uploading data to Google Sheets...")
        
        try:
            # Disable the button during upload
            self.root.config(cursor="wait")
            self.root.update()
            
            result = upload_to_sheets(
                json_file,
                spreadsheet_name,
                credentials_file,
                spreadsheet_id
            )
            
            self.root.config(cursor="")
            
            if result:
                self.status_var.set("Upload completed successfully")
            else:
                self.status_var.set("Upload failed")
        except Exception as e:
            messagebox.showerror("Error", f"Upload failed: {str(e)}")
            self.status_var.set("Upload failed")
            self.root.config(cursor="")
    
    def start_scraping(self):
        """Start the scraping process"""
        season = self.season_var.get()
        rule = self.rule_var.get()
        party = self.party_var.get()
        max_trainers = self.max_trainers_var.get()
        output_file = self.output_file_var.get()
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Disable start button
        self.start_button.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.status_var.set("Scraping in progress...")
        
        try:
            # Create scraper
            scraper = PokemonSVScraper()
            
            # Log start
            self.log(f"Starting scraper for Season {season}, Rule {rule}, Party {party}")
            self.log(f"Max trainers: {max_trainers}")
            
            # Get trainers with articles
            self.log("Fetching trainers with construction articles...")
            trainers = scraper.get_trainers_with_articles(season, rule, party)
            
            if not trainers:
                self.log("No trainers with articles found")
                messagebox.showinfo("Scraping Complete", "No trainers with articles found")
                self.start_button.config(state=tk.NORMAL)
                self.status_var.set("Ready")
                return
            
            self.log(f"Found {len(trainers)} trainers with construction articles")
            
            # Limit to max_trainers
            if max_trainers and len(trainers) > max_trainers:
                trainers = trainers[:max_trainers]
                self.log(f"Limited to {max_trainers} trainers")
            
            # Process trainers
            trainer_data = []
            total = len(trainers)
            
            for i, trainer in enumerate(trainers, 1):
                self.log(f"Processing trainer {i}/{total}: {trainer['trainer_name']} (Rank {trainer['rank']})")
                self.progress_var.set((i - 1) / total * 100)
                
                pokemon_list = []
                for pokemon_id in trainer['pokemon_ids']:
                    self.log(f"  Fetching details for Pokemon ID: {pokemon_id}")
                    # Try to get Pokemon details from the article
                    pokemon_data = scraper.get_pokemon_details_from_article(trainer['article_url'], pokemon_id)
                    
                    if pokemon_data:
                        pokemon_list.append(pokemon_data)
                        self.log(f"  Added {pokemon_data['name']}")
                    else:
                        self.log(f"  Failed to get data for Pokemon ID: {pokemon_id}")
                
                trainer_data.append({
                    'rank': trainer['rank'],
                    'rating': trainer['rating'],
                    'trainer_name': trainer['trainer_name'],
                    'article_url': trainer.get('article_url', ''),
                    'pokemon': pokemon_list
                })
                
                # Save progress periodically
                if i % 5 == 0 or i == total:
                    self.log(f"Saving progress after processing {i}/{total} trainers...")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(trainer_data, f, ensure_ascii=False, indent=2)
            
            # Save final results
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(trainer_data, f, ensure_ascii=False, indent=2)
            
            self.progress_var.set(100)
            self.log(f"Completed scraping {len(trainer_data)} trainers with construction articles")
            self.log(f"Data saved to {output_file}")
            
            messagebox.showinfo("Scraping Complete", f"Successfully scraped {len(trainer_data)} trainers.\nData saved to {output_file}")
            
            # Update JSON file in uploader tab
            self.json_file_var.set(output_file)
            
            # Switch to uploader tab
            self.tab_control.select(1)  # Select uploader tab
            
        except Exception as e:
            self.log(f"Error during scraping: {str(e)}")
            messagebox.showerror("Error", f"Scraping failed: {str(e)}")
        finally:
            # Re-enable start button
            self.start_button.config(state=tk.NORMAL)
            self.status_var.set("Ready")

def main():
    root = tk.Tk()
    app = PokemonSVUploaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 