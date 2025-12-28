-- Initialize PostgreSQL extensions
-- Run on database creation

-- Enable pgvector for embeddings (RAG)
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable PostGIS for spatial queries (pitch coordinates)
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
