#!/usr/bin/env python3
"""
KNOWLEDGE Database Setup Script

This script sets up the KNOWLEDGE database in Supabase using the schema defined in
setup_knowledge_database.sql. It uses the Supabase SQL Editor API to execute the SQL schema.
"""

import os
import sys
import json
import requests
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def read_sql_schema(file_path: str) -> str:
    """Read SQL schema from file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading SQL schema file: {e}")
        sys.exit(1)

def setup_knowledge_database():
    """Set up the KNOWLEDGE database."""
    print("Setting up KNOWLEDGE database in Supabase...")
    
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: Missing Supabase credentials in environment variables.")
        print("Please set SUPABASE_URL and SUPABASE_SERVICE_KEY.")
        sys.exit(1)
    
    # Path to the SQL schema
    schema_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "youtube-mcp-fork", "db", "setup_knowledge_database.sql"
    )
    
    # Read the SQL schema
    print(f"Reading SQL schema from {schema_path}...")
    sql_schema = read_sql_schema(schema_path)
    
    # First create the function for executing SQL
    execute_sql_func = """
    CREATE OR REPLACE FUNCTION execute_sql(query text)
    RETURNS json
    LANGUAGE plpgsql
    SECURITY DEFINER
    AS $$
    BEGIN
        EXECUTE query;
        RETURN json_build_object('success', true);
    EXCEPTION
        WHEN OTHERS THEN
        RETURN json_build_object(
            'success', false,
            'error', SQLERRM,
            'detail', SQLSTATE
        );
    END;
    $$;
    """
    
    try:
        # Open the Supabase dashboard to manually run the SQL schema
        project_id = supabase_url.split("//")[1].split(".")[0]
        dashboard_url = f"https://app.supabase.com/project/{project_id}/sql/new"
        
        print("\n===========================================================")
        print("IMPORTANT: Please set up the database manually using the SQL Editor:")
        print("1. Open this URL in your browser:")
        print(f"   {dashboard_url}")
        print("2. Copy and paste the SQL schema into the editor")
        print("3. Run the SQL commands")
        print("4. Verify the tables were created using verify_knowledge_db.py")
        print("===========================================================\n")
        
        # Save the SQL schema to a file for easy copying
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_schema.sql")
        with open(output_path, "w") as f:
            f.write(sql_schema)
        
        print(f"The SQL schema has been saved to: {output_path}")
        print("You can copy it from there and paste it into the SQL Editor.")
        
        # Ask if the user wants to open the browser
        user_input = input("Would you like to open the Supabase SQL Editor in your browser? (y/n): ")
        if user_input.lower() in ["y", "yes"]:
            import webbrowser
            webbrowser.open(dashboard_url)
            print("Browser opened to Supabase SQL Editor.")
        
        print("\nAfter running the SQL commands, run verify_knowledge_db.py to verify the setup.")
        
        print("KNOWLEDGE database setup completed. Verify with verify_knowledge_db.py")
        return True
    except Exception as e:
        print(f"Error in setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_knowledge_database()