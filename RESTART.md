# Restart Instructions for Supabase MCP Project

## To Resume with Claude Code

After reboot, open your terminal and run:

```
cd /Users/branchechols/supabase-mcp && claude
```

Then paste this message to Claude:

```
Let's continue our work on the Supabase KNOWLEDGE project. We previously:
1. Set up the database schema in Supabase
2. Created scripts for importing YouTube transcripts with context-aware chunking
3. Imported several videos on RAG techniques and Construction AI
4. Created query tools for searching the knowledge base

Our next task is to improve the search functionality and create a comprehensive summary of the Construction AI content in the database. Please check the status of our project and suggest the best way to continue.
```

## Key File Paths

- `/Users/branchechols/supabase-mcp/setup_knowledge_db.py` - Database setup script
- `/Users/branchechols/supabase-mcp/verify_knowledge_db.py` - Database verification
- `/Users/branchechols/supabase-mcp/fixed_import_transcript.py` - Import transcripts
- `/Users/branchechols/supabase-mcp/query_knowledge.py` - Search knowledge base
- `/Users/branchechols/supabase-mcp/list_videos.py` - List imported videos

## Useful Commands

- Verify database: `python3 /Users/branchechols/supabase-mcp/verify_knowledge_db.py`
- List videos: `python3 /Users/branchechols/supabase-mcp/list_videos.py`
- Search construction AI: `python3 /Users/branchechols/supabase-mcp/query_knowledge.py --query "construction AI" --limit 10`