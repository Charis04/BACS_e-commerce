#!/bin/bash
# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL service
service postgresql start

# Drop existing database and user if they exist
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -c "DROP USER IF EXISTS $DB_USER;"

# Modify pg_hba.conf to use trust authentication
cat <<EOL >/etc/postgresql/15/main/pg_hba.conf
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

# Apply migrations
if [ ! -d "migrations" ]; then
  flask db init # Initialize migrations if not already done
fi

flask db migrate -m "Initial migration with product table." # Create initial migration scripts
flask db upgrade                                            # Apply the migrations

# Seed initial data (optional)
python seed.py
