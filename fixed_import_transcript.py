#!/usr/bin/env python3
"""
Import YouTube Transcript to KNOWLEDGE Database

This script imports a YouTube transcript JSON file into the KNOWLEDGE database
in Supabase.
"""

import argparse
import json
import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def chunk_text(text, chunk_size=500, overlap=100):
    """Split text into chunks with overlap."""
    words = text.split()
    chunks = []
    
    if len(words) <= chunk_size:
        return [text]
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    
    return chunks

def import_transcript(transcript_json_path):
    """Import a YouTube transcript into the KNOWLEDGE database."""
    print(f"Importing transcript from {transcript_json_path}...")
    
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: Missing Supabase credentials in environment variables.")
        print("Please set SUPABASE_URL and SUPABASE_SERVICE_KEY.")
        sys.exit(1)
    
    # Read the transcript JSON
    try:
        with open(transcript_json_path, 'r', encoding='utf-8') as f:
            transcript_data = json.load(f)
    except Exception as e:
        print(f"Error reading transcript file: {e}")
        sys.exit(1)
    
    # Extract data from transcript
    video_id = transcript_data.get("video_id")
    video_url = transcript_data.get("video_url")
    title = transcript_data.get("title")
    channel = transcript_data.get("channel")
    upload_date = transcript_data.get("upload_date")
    description = transcript_data.get("description")
    transcript_text = transcript_data.get("transcript")
    extraction_time = transcript_data.get("extraction_time")
    
    # Connect to Supabase
    print(f"Connecting to Supabase at {supabase_url}...")
    try:
        supabase = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        sys.exit(1)
    
    # Create source record
    print(f"Creating source record for video: {title}...")
    source_data = {
        "source_type": "youtube",
        "title": title,
        "url": video_url,
        "author": channel,
        "published_date": upload_date,
        "description": description,
        "metadata": {
            "video_id": video_id,
            "extraction_time": extraction_time
        }
    }
    
    try:
        source_response = supabase.table("knowledge_sources").insert(source_data).execute()
        source_id = source_response.data[0]["id"]
        print(f"Created source with ID: {source_id}")
    except Exception as e:
        print(f"Error creating source record: {e}")
        sys.exit(1)
    
    # Create document record
    print("Creating document record...")
    document_data = {
        "source_id": source_id,
        "title": f"Transcript: {title}",
        "document_type": "transcript",
        "content": transcript_text,
        "metadata": {
            "video_id": video_id,
            "extraction_time": extraction_time
        }
    }
    
    try:
        document_response = supabase.table("knowledge_documents").insert(document_data).execute()
        document_id = document_response.data[0]["id"]
        print(f"Created document with ID: {document_id}")
    except Exception as e:
        print(f"Error creating document record: {e}")
        sys.exit(1)
    
    # Create YouTube video record
    print("Creating YouTube video record...")
    youtube_data = {
        "source_id": source_id,
        "youtube_id": video_id,
        "title": title,
        "channel": channel,
        "published_at": upload_date,
        "duration": 0,  # We don't have this information
        "transcript": transcript_text,
        "metadata": {
            "extraction_time": extraction_time
        }
    }
    
    try:
        # Check if the YouTube video record already exists
        check_response = supabase.table("youtube_videos").select("*").eq("youtube_id", video_id).execute()
        
        if check_response.data and len(check_response.data) > 0:
            print(f"YouTube video record already exists, skipping creation")
        else:
            youtube_response = supabase.table("youtube_videos").insert(youtube_data).execute()
            print(f"Created YouTube video record")
    except Exception as e:
        print(f"Warning: Issue with YouTube video record: {e}")
        print("Continuing with chunks...")
    
    # Split transcript into chunks
    print("Creating chunk records...")
    text_chunks = chunk_text(transcript_text)
    total_chunks = len(text_chunks)
    
    for i, chunk_content in enumerate(text_chunks):
        chunk_number = i + 1
        
        # Create context prefix and suffix
        context_prefix = text_chunks[i-1] if i > 0 else ""
        context_suffix = text_chunks[i+1] if i < total_chunks - 1 else ""
        
        # Create chunk record
        chunk_data = {
            "document_id": document_id,
            "content": chunk_content,
            "chunk_number": chunk_number,
            "total_chunks": total_chunks,
            "context_prefix": context_prefix,
            "context_suffix": context_suffix,
            "metadata": {
                "video_id": video_id,
                "extraction_time": extraction_time
            }
        }
        
        try:
            chunk_response = supabase.table("knowledge_chunks").insert(chunk_data).execute()
            print(f"Created chunk {chunk_number}/{total_chunks}")
        except Exception as e:
            print(f"Error creating chunk {chunk_number}: {e}")
            continue
    
    print(f"\nSuccessfully imported transcript for '{title}'")
    print(f"- Source ID: {source_id}")
    print(f"- Document ID: {document_id}")
    print(f"- Created {total_chunks} chunks")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import YouTube transcript to KNOWLEDGE database")
    parser.add_argument("transcript_json", help="Path to the transcript JSON file")
    
    args = parser.parse_args()
    
    import_transcript(args.transcript_json)