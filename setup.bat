:: filepath: /workspaces/ShopHive/setup.bat
@echo off
setlocal enabledelayedexpansion

:: Load environment variables from .env file
for /f "tokens=*" %%a in ('type .env ^| findstr /v "^#"') do (
    set %%a
)

:: Set pip cache directory
set PIP_CACHE_DIR=%TEMP%\pip-cache
if not exist %PIP_CACHE_DIR% mkdir %PIP_CACHE_DIR%

:: Remove existing virtual environment
if exist venv rmdir /s /q venv

:: Create and activate virtual environment
python -m venv venv
call venv\Scripts\activate.bat

:: Verify virtual environment
python -c "import sys; sys.exit(0 if sys.prefix != sys.base_prefix else 1)"
if errorlevel 1 (
    echo Failed to activate virtual environment
    exit /b 1
)

:: Install dependencies
python -m pip install --upgrade pip
python -m pip install flask
python -m pip install -r requirements.txt

:: Verify Flask installation
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Flask installation failed
    exit /b 1
)

:: PostgreSQL setup (assuming default installation path)
set PGBIN="C:\Program Files\PostgreSQL\15\bin"
set PGDATA="C:\Program Files\PostgreSQL\15\data"

:: Wait for PostgreSQL to be ready
:pgready
%PGBIN%\pg_isready
if errorlevel 1 (
    echo Waiting for PostgreSQL...
    timeout /t 1
    goto pgready
)

:: Database setup
%PGBIN%\psql -U postgres -c "DROP DATABASE IF EXISTS %DB_NAME%;"
%PGBIN%\psql -U postgres -c "DROP USER IF EXISTS %DB_USER%;"
%PGBIN%\psql -U postgres -c "CREATE USER %DB_USER% WITH SUPERUSER PASSWORD '%DB_PASS%';"
%PGBIN%\psql -U postgres -c "CREATE DATABASE %DB_NAME% OWNER %DB_USER%;"

:: Set permissions
%PGBIN%\psql -U postgres -d %DB_NAME% -c "ALTER SCHEMA public OWNER TO %DB_USER%;"
%PGBIN%\psql -U postgres -d %DB_NAME% -c "GRANT ALL ON SCHEMA public TO %DB_USER%;"
%PGBIN%\psql -U postgres -d %DB_NAME% -c "GRANT ALL ON ALL TABLES IN SCHEMA public TO %DB_USER%;"
%PGBIN%\psql -U postgres -d %DB_NAME% -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO %DB_USER%;"
%PGBIN%\psql -U postgres -d %DB_NAME% -c "GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO %DB_USER%;"

:: Clean up and reinitialize migrations
if exist migrations rmdir /s /q migrations
if exist flask_session rmdir /s /q flask_session
for /d /r %%d in (_pycache_) do @if exist "%%d" rd /s /q "%%d"

:: Initialize Flask migrations
set FLASK_APP=app.py
python -m flask db init
python -m flask db migrate -m "Initial migration including User.created_at"
python -m flask db upgrade

:: Seed initial data
python seed.py

echo Setup completed successfully
endlocal
