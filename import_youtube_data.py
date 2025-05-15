#!/usr/bin/env python3
"""
YouTube Data Import Script for KNOWLEDGE Database

This script imports YouTube transcripts into the KNOWLEDGE database in Supabase.
It processes transcripts extracted from YouTube videos and inserts them into
the appropriate tables in the database.
"""

import os
import sys
import json
import glob
from typing import Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def import_youtube_data(transcript_dir: str):
    """Import YouTube transcript data into the KNOWLEDGE database."""
    print(f"Importing YouTube data from {transcript_dir}...")
    
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
    
    # Find all transcript JSON files
    transcript_files = glob.glob(os.path.join(transcript_dir, "*.json"))
    if not transcript_files:
        print(f"No transcript files found in {transcript_dir}")
        sys.exit(1)
    
    print(f"Found {len(transcript_files)} transcript files")
    
    # Process each transcript file
    for transcript_file in transcript_files:
        video_id = os.path.basename(transcript_file).replace(".json", "")
        print(f"\nProcessing video {video_id}...")
        
        # Read transcript data
        try:
            with open(transcript_file, 'r', encoding='utf-8') as f:
                transcript_data = json.load(f)
        except Exception as e:
            print(f"Error reading transcript file {transcript_file}: {e}")
            continue
        
        video_info = transcript_data.get("video_info", {})
        chunks = transcript_data.get("chunks", [])
        
        if not video_info or not chunks:
            print(f"Invalid transcript data in {transcript_file}")
            continue
        
        # Create source record
        source_data = {
            "source_type": "youtube",
            "title": video_info.get("title", "Unknown"),
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "author": video_info.get("channel", "Unknown"),
            "published_date": video_info.get("upload_date", ""),
            "description": video_info.get("description", ""),
            "metadata": {
                "video_id": video_id,
                "duration": video_info.get("duration", 0),
                "view_count": video_info.get("view_count", 0)
            }
        }
        
        print(f"Creating source record for '{source_data['title']}'...")
        try:
            source_response = supabase.table("knowledge_sources").insert(source_data).execute()
            source_id = source_response.data[0]["id"]
        except Exception as e:
            print(f"Error creating source record: {e}")
            continue
        
        # Create document record
        document_data = {
            "source_id": source_id,
            "title": f"Transcript: {video_info.get('title', 'Unknown')}",
            "document_type": "transcript",
            "content": "".join([chunk.get("text", "") for chunk in chunks]),
            "metadata": {
                "video_id": video_id,
                "duration": video_info.get("duration", 0),
                "chunk_count": len(chunks)
            }
        }
        
        print(f"Creating document record...")
        try:
            document_response = supabase.table("knowledge_documents").insert(document_data).execute()
            document_id = document_response.data[0]["id"]
        except Exception as e:
            print(f"Error creating document record: {e}")
            continue
        
        # Create chunk records
        print(f"Creating {len(chunks)} chunk records...")
        total_chunks = len(chunks)
        
        for i, chunk in enumerate(chunks):
            chunk_number = i + 1
            
            # Get context prefix and suffix
            context_prefix = ""
            if i > 0:
                context_prefix = chunks[i-1].get("text", "")
            
            context_suffix = ""
            if i < total_chunks - 1:
                context_suffix = chunks[i+1].get("text", "")
            
            chunk_data = {
                "document_id": document_id,
                "content": chunk.get("text", ""),
                "chunk_number": chunk_number,
                "total_chunks": total_chunks,
                "context_prefix": context_prefix,
                "context_suffix": context_suffix,
                "metadata": {
                    "start_time": chunk.get("start", 0),
                    "end_time": chunk.get("end", 0),
                    "duration": chunk.get("end", 0) - chunk.get("start", 0)
                }
            }
            
            try:
                chunk_response = supabase.table("knowledge_chunks").insert(chunk_data).execute()
                if chunk_number % 10 == 0:
                    print(f"  Created {chunk_number}/{total_chunks} chunks...")
            except Exception as e:
                print(f"Error creating chunk record {chunk_number}: {e}")
                continue
        
        # Create YouTube-specific record
        youtube_data = {
            "source_id": source_id,
            "youtube_id": video_id,
            "title": video_info.get("title", "Unknown"),
            "channel": video_info.get("channel", "Unknown"),
            "published_at": video_info.get("upload_date", ""),
            "duration": video_info.get("duration", 0),
            "transcript": document_data["content"],
            "metadata": {
                "view_count": video_info.get("view_count", 0),
                "like_count": video_info.get("like_count", 0),
                "comment_count": video_info.get("comment_count", 0)
            }
        }
        
        print(f"Creating YouTube-specific record...")
        try:
            youtube_response = supabase.table("youtube_videos").insert(youtube_data).execute()
        except Exception as e:
            print(f"Error creating YouTube record: {e}")
            continue
        
        print(f"Finished processing video {video_id}!")
    
    print("\nYouTube data import complete!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_youtube_data.py <transcript_directory>")
        sys.exit(1)
    
    transcript_dir = sys.argv[1]
    import_youtube_data(transcript_dir)