#!/bin/bash
# Install dependencies
pip install -r requirements.txt

# Apply migrations
flask db upgrade

# Seed initial data (optional)
python seed.py
