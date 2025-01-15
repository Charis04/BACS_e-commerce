#!/bin/bash
set -e  # Exit on error

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Set pip cache directory to avoid permission issues
export PIP_CACHE_DIR=/tmp/pip-cache
mkdir -p $PIP_CACHE_DIR

# Remove existing virtual environment if it exists
rm -rf venv

# Create and activate virtual environment with explicit python version
python3 -m venv venv
. venv/bin/activate

# Verify we're in the virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Failed to activate virtual environment"
    exit 1
fi

# Install dependencies in virtual environment
python -m pip install --upgrade pip
python -m pip install flask
python -m pip install -r requirements.txt

# Verify flask installation
if ! python -c "import flask" 2>/dev/null; then
    echo "Flask installation failed"
    exit 1
fi

# Start PostgreSQL service and wait for it to be ready
service postgresql start
sleep 2

# Ensure PostgreSQL is running
until pg_isready; do
    echo "Waiting for PostgreSQL to be ready..."
    sleep 1
done

# Drop existing database and user if they exist
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -c "DROP USER IF EXISTS $DB_USER;"

# Modify pg_hba.conf with direct write (we're root)
cat > /etc/postgresql/15/main/pg_hba.conf << EOL
# "local" is for Unix domain socket connections only
local   all             all                                     trust

# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
# IPv6 local connections:
host    all             all             ::1/128                 md5
EOL

# Reload PostgreSQL configuration to apply changes
service postgresql reload

# Set postgres user password
PGPASSWORD='' psql -U postgres -c "ALTER USER postgres PASSWORD '$POSTGRES_PASSWORD';"

# Revert pg_hba.conf back to md5 authentication
cat <<EOL >/etc/postgresql/15/main/pg_hba.conf
# "local" is for Unix domain socket connections only
local   all             all                                     md5

# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
# IPv6 local connections:
host    all             all             ::1/128                 md5
EOL

# Reload PostgreSQL configuration to apply changes
service postgresql reload

# Setup PostgreSQL database and user using environment variables
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -c "CREATE DATABASE $DB_NAME;"
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# Grant privileges on the public schema
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -d $DB_NAME -c "GRANT ALL PRIVILEGES ON SCHEMA public TO $DB_USER;"
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;"
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -d $DB_NAME -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;"

# Drop and recreate database with clean slate
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -c "DROP USER IF EXISTS $DB_USER;"
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -c "CREATE USER $DB_USER WITH SUPERUSER PASSWORD '$DB_PASS';"
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# Set ownership and permissions
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -d $DB_NAME -c "ALTER SCHEMA public OWNER TO $DB_USER;"
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -d $DB_NAME -c "GRANT ALL ON ALL TABLES IN SCHEMA public TO $DB_USER;"
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -d $DB_NAME -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;"
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -d $DB_NAME -c "GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO $DB_USER;"

# Clean up and reinitialize migrations
rm -rf migrations flask_session/* __pycache__
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true

# Initialize Flask migrations with force
export FLASK_APP=app.py
rm -rf migrations/
python -m flask db init
python -m flask db migrate -m "Initial migration including User.created_at"
python -m flask db upgrade

# Install the package in development mode
# python -m pip install -e .
# Seed initial data
python seed.py

echo "Setup completed successfully"
