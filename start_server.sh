#!/bin/bash

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "$DIR/venv/bin/activate"

# Set environment variables if they're not already set
export SUPABASE_URL=${SUPABASE_URL:-"https://jdtfqobmopcqqktpaxaa.supabase.co"}
export SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY:-"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpkdGZxb2Jtb3BjcXFrdHBheGFhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzA0NDM0NSwiZXhwIjoyMDYyNjIwMzQ1fQ.rfEtj6omqAZKSuoPPl2JVPM7WwybaYXE77OKLbqLrr8"}

# Start the Supabase MCP server
cd "$DIR/supabase_mcp"
exec python server.py