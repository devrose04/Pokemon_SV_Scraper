"""
Script to build the executable for the Pokemon SV Trainer Data Scraper.
This will create a standalone executable file that can be distributed.

ポケモンSVトレーナーデータスクレイパーの実行ファイルをビルドするためのスクリプト。
配布可能なスタンドアロンの実行ファイルを作成します。
"""

import os
import sys
import subprocess
import shutil

def install_requirements():
    """Install the required packages for building the executable.
    実行ファイルをビルドするために必要なパッケージをインストールします。
    """
    print("Installing required packages... / 必要なパッケージをインストールしています...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "pillow"])
    
    # Check if the requirements.txt file exists and install those requirements
    # requirements.txtファイルが存在する場合、それらの要件をインストールします
    if os.path.exists("requirements.txt"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def create_icon():
    """Create the icon for the application if it doesn't exist.
    アプリケーションのアイコンが存在しない場合、作成します。
    """
    if not os.path.exists("pokemon_icon.ico"):
        print("Creating application icon... / アプリケーションアイコンを作成しています...")
        try:
            # Try to import the create_icon module
            # create_iconモジュールをインポートしようとします
            from create_icon import create_pokeball_icon
            create_pokeball_icon()
        except ImportError:
            print("Warning: Could not create icon. The create_icon.py file may be missing. / 警告: アイコンを作成できませんでした。create_icon.pyファイルが見つかりません。")
            print("The application will use the default icon. / アプリケーションはデフォルトのアイコンを使用します。")

def build_executable():
    """Build the executable using PyInstaller.
    PyInstallerを使用して実行ファイルをビルドします。
    """
    print("Building executable for Pokemon SV Scraper GUI... / ポケモンSVスクレイパーGUIの実行ファイルをビルドしています...")
    
    # Ensure we're using the virtual environment python
    # 仮想環境のpythonを使用していることを確認します
    python_exe = os.path.join('.venv', 'Scripts', 'python')
    
    # Run PyInstaller
    # PyInstallerを実行
    cmd = [
        python_exe, 
        '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--icon=pokemon_icon.ico',
        '--name=Pokemon_SV_Scraper',
        'gui_app.py'
    ]
    
    print(f"Running command: {' '.join(cmd)} / コマンドを実行しています")
    subprocess.run(cmd, check=True)
    
    # Create a dist folder with all necessary files
    # 必要なファイルをすべて含むdistフォルダを作成
    print("Copying necessary files to dist folder... / 必要なファイルをdistフォルダにコピーしています...")
    required_files = [
        'credentials_template.json',
        'create_credentials.py',
        'main.py',
        'sheets_uploader.py',
        'test_sheets.py',
        'pokemon_icon.ico',
        'README.md'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            shutil.copy(file, os.path.join('dist', file))
            print(f"Copied {file} to dist folder / {file}をdistフォルダにコピーしました")
        else:
            print(f"Warning: {file} not found, skipping / 警告: {file}が見つかりません、スキップします")
    
    print("\nBuild complete! The executable and all necessary files are in the 'dist' folder. / ビルド完了！実行ファイルと必要なファイルはすべて'dist'フォルダにあります。")
    print("To use the application, distribute the entire 'dist' folder. / アプリケーションを使用するには、'dist'フォルダ全体を配布してください。")

def main():
    """Main function to build the executable.
    実行ファイルをビルドするためのメイン関数。
    """
    print("Building Pokemon SV Trainer Data Scraper executable... / ポケモンSVトレーナーデータスクレイパーの実行ファイルをビルドしています...")
    
    # Install required packages
    # 必要なパッケージをインストール
    install_requirements()
    
    # Create the icon
    # アイコンを作成
    create_icon()
    
    # Build the executable
    # 実行ファイルをビルド
    build_executable()
    
    print("Done! / 完了！")

if __name__ == "__main__":
    main() 