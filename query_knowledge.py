#!/usr/bin/env python3
"""
Query KNOWLEDGE Database

This script queries the KNOWLEDGE database in Supabase to retrieve information.
"""

import argparse
import json
import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def query_knowledge(query, limit=5):
    """Query the KNOWLEDGE database."""
    print(f"Querying KNOWLEDGE database for: {query}")
    
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
    
    # Query for related chunks
    print(f"Searching for chunks related to: {query}")
    try:
        # For now, we'll do a simple text search since we don't have embeddings yet
        search_term = f"%{query}%"
        chunks_response = supabase.table("knowledge_chunks") \
            .select("*, knowledge_documents(title)") \
            .ilike("content", search_term) \
            .limit(limit) \
            .execute()
        
        chunks = chunks_response.data
        print(f"Found {len(chunks)} related chunks")
        
        if not chunks:
            print("No results found.")
            return
        
        # Display the results
        print("\n===== SEARCH RESULTS =====\n")
        for i, chunk in enumerate(chunks):
            doc_title = chunk["knowledge_documents"]["title"] if chunk["knowledge_documents"] else "Unknown"
            print(f"Result {i+1} from: {doc_title}")
            print(f"Chunk {chunk['chunk_number']}/{chunk['total_chunks']}")
            print("-" * 40)
            print(chunk["content"])
            print("-" * 40)
            print()
        
    except Exception as e:
        print(f"Error querying database: {e}")
        sys.exit(1)

def list_all_documents():
    """List all documents in the KNOWLEDGE database."""
    print("Listing all documents in KNOWLEDGE database")
    
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
    
    # Query for all documents
    try:
        docs_response = supabase.table("knowledge_documents") \
            .select("*, knowledge_sources(title, source_type)") \
            .execute()
        
        documents = docs_response.data
        print(f"Found {len(documents)} documents")
        
        if not documents:
            print("No documents found.")
            return
        
        # Display the results
        print("\n===== DOCUMENTS =====\n")
        for i, doc in enumerate(documents):
            source_title = doc["knowledge_sources"]["title"] if doc["knowledge_sources"] else "Unknown"
            source_type = doc["knowledge_sources"]["source_type"] if doc["knowledge_sources"] else "Unknown"
            
            print(f"Document {i+1}: {doc['title']}")
            print(f"Source: {source_title} ({source_type})")
            print(f"Type: {doc['document_type']}")
            print(f"Created: {doc['created_at']}")
            print("-" * 40)
            print()
        
    except Exception as e:
        print(f"Error listing documents: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query KNOWLEDGE database")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--limit", "-l", type=int, default=5, help="Maximum number of results")
    parser.add_argument("--list-docs", "-d", action="store_true", help="List all documents")
    
    args = parser.parse_args()
    
    if args.list_docs:
        list_all_documents()
    elif args.query:
        query_knowledge(args.query, args.limit)
    else:
        parser.print_help()