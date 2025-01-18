#!/bin/bash
set -e  # Exit on error

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Set pip cache directory
export PIP_CACHE_DIR=/tmp/pip-cache
mkdir -p $PIP_CACHE_DIR

# Remove existing virtual environment if it exists
rm -rf venv

# Create and activate virtual environment
python3 -m venv venv
. venv/bin/activate

# Verify we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Failed to activate virtual environment"
    exit 1
fi

# Install dependencies
python -m pip install --upgrade pip
python -m pip install flask flask-sqlalchemy flask-migrate
python -m pip install -r requirements.txt

# Install package in development mode
python -m pip install -e .

# PostgreSQL setup
echo "Configuring PostgreSQL..."
# Start PostgreSQL service
service postgresql start

# Wait for PostgreSQL to be ready
until pg_isready; do
    echo "Waiting for PostgreSQL to start..."
    sleep 1
done

# Drop existing database and user if they exist
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -c "DROP USER IF EXISTS $DB_USER;"

# Configure PostgreSQL to accept connections with trust auth temporarily
cat > /etc/postgresql/*/main/pg_hba.conf << EOL
# "local" is for Unix domain socket connections only
local   all             all                                     trust

# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
# IPv6 local connections:
host    all             all             ::1/128                 md5
EOL

# Reload PostgreSQL configuration
service postgresql reload

# Set postgres user password
PGPASSWORD='' psql -U postgres -c "ALTER USER postgres PASSWORD '$POSTGRES_PASSWORD';"

# Revert pg_hba.conf back to md5 authentication
cat > /etc/postgresql/*/main/pg_hba.conf << EOL
# "local" is for Unix domain socket connections only
local   all             all                                     md5

# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
# IPv6 local connections:
host    all             all             ::1/128                 md5
EOL

# Reload PostgreSQL configuration
service postgresql reload

# Setup database and user
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -c "CREATE DATABASE $DB_NAME;"
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Grant schema privileges
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"

# Set Flask environment variable
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    set FLASK_APP=app
else
    export FLASK_APP=app
fi

# Create a temporary Python script for database initialization
cat > init_db.py << EOL
from shophive_packages import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
EOL

# Initialize database
python init_db.py

# Remove temporary script
rm init_db.py

# Run seed script
python seed.py

echo "Setup completed successfully! Database has been initialized and seeded."
