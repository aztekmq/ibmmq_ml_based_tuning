#!/bin/bash

# Name of the SQLite database
DB_NAME="server_analysis.db"

# Check if sqlite3 is installed
if ! command -v sqlite3 &> /dev/null; then
    echo "sqlite3 is not installed. Please install it and try again."
    exit 1
fi

# Create the database and the tables
sqlite3 $DB_NAME <<EOF
CREATE TABLE IF NOT EXISTS metrics_collector (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cpu_usage FLOAT,
    memory_usage INTEGER,
    disk_usage TEXT
);

CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cpu_usage FLOAT,
    memory_usage INTEGER,
    recommendation TEXT
);
EOF

# Check if the tables were created successfully
if [ $? -eq 0 ]; then
    echo "Database and tables created successfully in $DB_NAME"
else
    echo "There was an error creating the database or tables."
fi
