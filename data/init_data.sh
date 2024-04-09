#!/bin/bash

# Check if marker file exists
if [ ! -f "/var/lib/postgresql/data/initialized" ]; then
    echo "Initializing PostgreSQL database..."
    
    # Execute the SQL initialization script
    psql -U postgres -d dataflix -f /init.sql
    
    # Create a marker file to indicate initialization
    touch "/var/lib/postgresql/data/initialized"
fi

# Start PostgreSQL service
exec postgres