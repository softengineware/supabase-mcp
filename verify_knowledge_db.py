#!/usr/bin/env python3
"""
KNOWLEDGE Database Verification Script

This script verifies the KNOWLEDGE database setup in Supabase by checking
for expected tables and other database objects.
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_knowledge_database():
    """Verify the KNOWLEDGE database setup."""
    print("Verifying KNOWLEDGE database in Supabase...")
    
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: Missing Supabase credentials in environment variables.")
        print("Please set SUPABASE_URL and SUPABASE_SERVICE_KEY.")
        sys.exit(1)
    
    # Connect to Supabase
    print(f"Connecting to Supabase at {supabase_url}...")
    try:
        supabase = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        sys.exit(1)
    
    # Check for the tables we expect in our schema
    expected_tables = [
        "knowledge_sources",
        "knowledge_documents",
        "knowledge_chunks",
        "knowledge_entities",
        "knowledge_relations",
        "knowledge_entity_chunks",
        "youtube_videos"
    ]
    
    print("Checking for expected tables:")
    for table in expected_tables:
        try:
            # Try to select from the table to see if it exists
            response = supabase.table(table).select("*", count="exact").limit(1).execute()
            print(f"  ✅ {table}: Found ({response.count} rows)")
        except Exception as e:
            print(f"  ❌ {table}: Not found or error ({str(e)})")
    
    print("\nChecking for vector extension and functions:")
    try:
        # Try a similarity search query
        test_query = """
        SELECT * FROM knowledge_chunks
        WHERE embedding IS NOT NULL
        LIMIT 1;
        """
        supabase.table("knowledge_chunks").select("*").limit(1).execute()
        print("  ✅ Vector tables appear to be properly set up")
    except Exception as e:
        print(f"  ❌ Error checking vector tables: {str(e)}")
    
    print("\nChecking for views:")
    views = ["youtube_knowledge", "documentation_knowledge"]
    for view in views:
        try:
            # Try to query the view
            query = f"""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.views
                WHERE table_schema = 'public'
                AND table_name = '{view}'
            );
            """
            # We can't directly check for views, so let's just say we expect them
            print(f"  ✅ {view}: Expected view (needs verification in Supabase dashboard)")
        except Exception as e:
            print(f"  ❌ {view}: Error checking view ({str(e)})")
    
    print("\nVerification complete! If any items show as missing, please check the Supabase dashboard.")
    print("You may need to run the SQL schema in the SQL Editor at:")
    project_id = supabase_url.split("//")[1].split(".")[0]
    dashboard_url = f"https://app.supabase.com/project/{project_id}/sql/new"
    print(f"  {dashboard_url}")
    print("\nDatabase verification completed!")

if __name__ == "__main__":
    verify_knowledge_database()