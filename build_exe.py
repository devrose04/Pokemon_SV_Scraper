import os
import sys
import shutil
import PyInstaller.__main__

def build_exe():
    """Build the executable using PyInstaller"""
    
    # Clean up previous build directories
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    # PyInstaller options
    options = [
        'pokemon_sv_uploader.py',  # Main script (updated)
        '--name=Pokemon_SV_Uploader',
        '--onefile',
        '--noconsole',
        '--icon=pokemon_icon.ico',
        '--add-data=credentials.json;.',
        '--add-data=sample_trainer_data.json;.',  # Include sample data
        '--hidden-import=requests',
        '--hidden-import=bs4',
        '--hidden-import=google.oauth2.service_account',
        '--hidden-import=googleapiclient.discovery',
        '--hidden-import=googleapiclient.errors',
        '--hidden-import=tkinter',
    ]
    
    # Run PyInstaller
    PyInstaller.__main__.run(options)
    print("Build completed! You can find the executable in the 'dist' directory.")

if __name__ == "__main__":
    build_exe() 