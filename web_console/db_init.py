#!/usr/bin/python3

from web_console import db

# Create all tables
db.create_all()

print("Database initialized successfully!")
