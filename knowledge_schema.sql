-- KNOWLEDGE Database Schema
-- Based on insights from Cole Medin's YouTube tutorials on RAG techniques

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Sources table - tracks where knowledge comes from
CREATE TABLE knowledge_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type TEXT NOT NULL, -- 'youtube', 'documentation', 'website', etc.
    title TEXT NOT NULL,
    url TEXT,
    author TEXT,
    published_date TIMESTAMP,
    description TEXT,
    metadata JSONB, -- For source-specific metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documents table - represents a single document from a source
CREATE TABLE knowledge_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES knowledge_sources(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    document_type TEXT NOT NULL, -- 'transcript', 'article', 'api_doc', 'tutorial', etc.
    content TEXT, -- Full document content for reference
    metadata JSONB, -- For document-specific metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chunks table - smaller pieces of documents for retrieval
CREATE TABLE knowledge_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(1536), -- For OpenAI embeddings
    chunk_number INTEGER, -- Sequence in document
    total_chunks INTEGER, -- Total number of chunks in document
    -- Fields for contextual embedding from "The EASIEST Possible Strategy for Accurate RAG"
    context_prefix TEXT, -- Additional context prepended before embedding
    context_suffix TEXT, -- Additional context appended before embedding
    -- Fields inspired by "LightRAG" from "The PROVEN Solution for Unbelievable RAG Performance"
    entities JSONB, -- Key entities extracted from chunk
    relations JSONB, -- Relationships between entities
    metadata JSONB, -- Additional metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create a GIN index on entities and relations for faster lookups
CREATE INDEX IF NOT EXISTS knowledge_chunks_entities_idx ON knowledge_chunks USING GIN (entities);
CREATE INDEX IF NOT EXISTS knowledge_chunks_relations_idx ON knowledge_chunks USING GIN (relations);

-- Create a vector index on embeddings for similarity search
CREATE INDEX IF NOT EXISTS knowledge_chunks_embedding_idx ON knowledge_chunks 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Knowledge graph tables - based on LightRAG approach
CREATE TABLE knowledge_entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL, -- 'person', 'concept', 'tool', 'framework', etc.
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE knowledge_relations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_entity_id UUID REFERENCES knowledge_entities(id) ON DELETE CASCADE,
    target_entity_id UUID REFERENCES knowledge_entities(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL, -- 'is_a', 'part_of', 'uses', 'created_by', etc.
    weight FLOAT DEFAULT 1.0,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Entity-Chunk associations
CREATE TABLE knowledge_entity_chunks (
    entity_id UUID REFERENCES knowledge_entities(id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES knowledge_chunks(id) ON DELETE CASCADE,
    relevance_score FLOAT,
    PRIMARY KEY (entity_id, chunk_id)
);

-- YouTube-specific table
CREATE TABLE youtube_videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES knowledge_sources(id) ON DELETE CASCADE,
    youtube_id TEXT NOT NULL UNIQUE, -- YouTube video ID
    title TEXT NOT NULL,
    channel TEXT,
    published_at TIMESTAMP,
    duration INTEGER, -- in seconds
    transcript TEXT,
    metadata JSONB, -- Video-specific metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Functions for updating the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for each table
CREATE TRIGGER update_knowledge_sources_updated_at
BEFORE UPDATE ON knowledge_sources
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_knowledge_documents_updated_at
BEFORE UPDATE ON knowledge_documents
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_knowledge_chunks_updated_at
BEFORE UPDATE ON knowledge_chunks
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_knowledge_entities_updated_at
BEFORE UPDATE ON knowledge_entities
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_knowledge_relations_updated_at
BEFORE UPDATE ON knowledge_relations
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_youtube_videos_updated_at
BEFORE UPDATE ON youtube_videos
FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Function for contextual similarity search
CREATE OR REPLACE FUNCTION search_knowledge_contextual(
    query_text TEXT,
    similarity_threshold FLOAT DEFAULT 0.7,
    max_results INTEGER DEFAULT 10,
    filter_source_type TEXT DEFAULT NULL
)
RETURNS TABLE (
    chunk_id UUID,
    document_id UUID,
    source_id UUID,
    content TEXT,
    context_prefix TEXT,
    context_suffix TEXT,
    similarity FLOAT,
    source_type TEXT,
    title TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    query_embedding vector(1536);
BEGIN
    -- Generate embedding for query using OpenAI embedding function (to be implemented)
    -- For this SQL, assume query_embedding is provided

    RETURN QUERY
    SELECT 
        kc.id as chunk_id,
        kc.document_id,
        kd.source_id,
        kc.content,
        kc.context_prefix,
        kc.context_suffix,
        1 - (kc.embedding <=> query_embedding) as similarity,
        ks.source_type,
        kd.title
    FROM knowledge_chunks kc
    JOIN knowledge_documents kd ON kc.document_id = kd.id
    JOIN knowledge_sources ks ON kd.source_id = ks.id
    WHERE 
        (filter_source_type IS NULL OR ks.source_type = filter_source_type) AND
        1 - (kc.embedding <=> query_embedding) > similarity_threshold
    ORDER BY similarity DESC
    LIMIT max_results;
END;
$$;

-- Create view for YouTube content
CREATE OR REPLACE VIEW youtube_knowledge AS
SELECT 
    ks.id AS source_id,
    ks.title AS source_title,
    kd.id AS document_id,
    kd.title AS document_title,
    yv.youtube_id,
    yv.channel,
    yv.published_at,
    kc.id AS chunk_id,
    kc.content AS chunk_content,
    kc.context_prefix,
    kc.context_suffix,
    kc.chunk_number,
    kc.total_chunks
FROM youtube_videos yv
JOIN knowledge_sources ks ON yv.source_id = ks.id
JOIN knowledge_documents kd ON ks.id = kd.source_id
JOIN knowledge_chunks kc ON kd.id = kc.document_id
ORDER BY yv.published_at DESC, kc.chunk_number;

-- Create view for documentation content
CREATE OR REPLACE VIEW documentation_knowledge AS
SELECT 
    ks.id AS source_id,
    ks.title AS source_title,
    ks.author,
    kd.id AS document_id,
    kd.title AS document_title,
    kd.document_type,
    kc.id AS chunk_id,
    kc.content AS chunk_content,
    kc.context_prefix,
    kc.context_suffix,
    kc.entities,
    kc.relations
FROM knowledge_sources ks
JOIN knowledge_documents kd ON ks.id = kd.source_id
JOIN knowledge_chunks kc ON kd.id = kc.document_id
WHERE ks.source_type = 'documentation'
ORDER BY ks.title, kd.title, kc.chunk_number;