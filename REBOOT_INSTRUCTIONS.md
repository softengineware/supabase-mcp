# Supabase MCP Project - Reboot Instructions

## Claude CLI Command to Restart Session

Copy and paste this command to Claude CLI after reboot:

```
cd /Users/branchechols/supabase-mcp && claude
```

## Project Status

We've successfully set up a Supabase KNOWLEDGE database project with the following components:

1. Database schema for storing and retrieving knowledge from various sources
2. Scripts for setting up and verifying the database structure
3. Tools for importing YouTube transcripts with context-aware chunking
4. Utilities for listing videos and querying the knowledge base
5. Transcript data from various YouTube videos on RAG techniques and Construction AI

## To Continue After Reboot (Copy-Paste Commands)

1. **Navigate to project directory:**
   ```
   cd /Users/branchechols/supabase-mcp
   ```

2. **Start the Supabase MCP server:**
   ```
   ./start_server.sh
   ```

3. **Verify database connectivity:**
   ```
   python3 /Users/branchechols/supabase-mcp/verify_knowledge_db.py
   ```

4. **List imported videos:**
   ```
   python3 /Users/branchechols/supabase-mcp/list_videos.py
   ```

5. **Query the knowledge base for Construction AI content:**
   ```
   python3 /Users/branchechols/supabase-mcp/query_knowledge.py --query "construction AI" --limit 10
   ```

6. **Search for specific Construction AI topics:**
   ```
   python3 /Users/branchechols/supabase-mcp/query_knowledge.py --query "AI in construction benefits" --limit 5
   ```

## Available Scripts with Full Paths

- `/Users/branchechols/supabase-mcp/setup_knowledge_db.py` - Set up the KNOWLEDGE database schema
- `/Users/branchechols/supabase-mcp/verify_knowledge_db.py` - Verify database tables and structure
- `/Users/branchechols/supabase-mcp/fixed_import_transcript.py` - Import transcripts with context handling
- `/Users/branchechols/supabase-mcp/list_videos.py` - List videos stored in the database
- `/Users/branchechols/supabase-mcp/query_knowledge.py` - Search the knowledge base for information
- `/Users/branchechols/supabase-mcp/start_server.sh` - Start the Supabase MCP server

## Repository Status

All changes have been committed locally to the supabase-mcp repository. No changes have been pushed to remote repositories.

## Next Tasks

1. Improve the search functionality in `query_knowledge.py` to extract more relevant information
2. Create a comprehensive summary of the Construction AI content
3. Explore implementation of vector embeddings for semantic search