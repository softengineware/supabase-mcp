#!/usr/bin/env python3
"""
List YouTube Videos in KNOWLEDGE Database

This script lists all YouTube videos stored in the KNOWLEDGE database.
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

# Connect to Supabase
supabase = create_client(supabase_url, supabase_key)

# Query YouTube videos
response = supabase.table("youtube_videos").select("*").execute()

# Display results
print(f"Found {len(response.data)} videos:")
for video in response.data:
    print(f"- {video['title']} (ID: {video['youtube_id']})")
    print(f"  Channel: {video['channel']}")
    print(f"  Published: {video['published_at']}")
    print()