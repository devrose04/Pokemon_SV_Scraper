@echo off
echo Starting Pokemon SV Trainer Data Scraper... / ポケモンSVトレーナーデータスクレイパーを起動しています...
echo.

REM Activate the virtual environment if it exists / 仮想環境が存在する場合はアクティブ化
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found. Using system Python. / 警告: 仮想環境が見つかりません。システムのPythonを使用します。
)

REM Run the GUI application / GUIアプリケーションを実行
python gui_app.py

echo.
echo Application closed. / アプリケーションが終了しました。
echo.

REM Pause to see the output / 出力を確認するための一時停止
pause 