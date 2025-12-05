# KB-Admin Service

Knowledge Base Management Microservice for Agent-Specific Knowledge Bases with Self-Learning Capabilities

## Overview

KB-Admin is a FastAPI-based microservice that manages agent-specific knowledge bases using Redis Stack for vector storage and MySQL for metadata. It provides:

- **Agent-Specific Knowledge Bases**: Separate vector indexes for each agent type
- **Document Management**: Upload, chunk, and vectorize documents (markdown, text, PDF)
- **Self-Learning System**: Automatically capture and vectorize approved Q&A pairs, solutions, and corrections
- **Configuration-Driven Integration**: Minimal changes to existing agents required

## Architecture

```
kb-admin/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # MySQL connection pool
│   ├── redis_client.py      # Redis connection & index operations
│   ├── models/              # Pydantic models
│   │   ├── knowledge_base.py
│   │   └── document.py
│   ├── services/            # Business logic
│   │   ├── redis_index_service.py
│   │   ├── embedding_service.py
│   │   └── vectorization_service.py (TODO)
│   ├── api/                 # API routes (TODO)
│   │   ├── kb_routes.py
│   │   └── document_routes.py
│   └── utils/               # Utilities
│       └── chunking.py
├── migrations/              # SQL migrations
│   ├── 001_create_knowledge_bases_table.sql
│   ├── 002_create_kb_documents_table.sql
│   ├── 003_create_learned_knowledge_table.sql
│   ├── 004_create_kb_audit_log_table.sql
│   └── run_migrations.py
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Technology Stack

- **Backend**: FastAPI 0.109.0 + Uvicorn
- **Database**: MySQL 8.x (shared with Laravel main-app)
- **Vector Store**: Redis Stack (with RediSearch module)
- **Embeddings**: OpenAI (text-embedding-3-small) / Anthropic
- **Text Processing**: LangChain for document chunking

## Database Schema

### knowledge_bases
- Stores KB metadata (agent_type, name, status, embedding config)
- Unique constraint: one active KB per agent_type

### kb_documents
- Stores document content and vectorization status
- Foreign key to knowledge_bases

### learned_knowledge
- Stores self-learned Q&A pairs, solutions, corrections
- Requires admin approval before vectorization

### kb_audit_log
- Tracks all KB operations (created, vectorized, activated, etc.)

## Redis Indexes

- **Naming Convention**: `kb_{agent_type}`
  - `kb_requirement_agent`
  - `kb_developer_agent`
  - `kb_generic`

- **Index Schema**:
  - Text fields: content, title
  - Numeric: document_id, kb_id, chunk_index
  - Vector: embedding (1536 dims for OpenAI, 1024 for Anthropic)
  - Algorithm: HNSW with COSINE distance

## Environment Variables

See `.env.example` for full configuration.

**Required**:
- `DB_HOST`, `DB_USERNAME`, `DB_PASSWORD`, `DB_DATABASE`
- `REDIS_URL`
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

**Optional**:
- `DEFAULT_CHUNK_SIZE` (default: 1000)
- `DEFAULT_CHUNK_OVERLAP` (default: 200)
- `MAX_UPLOAD_SIZE` (default: 10MB)

## Setup & Installation

### Docker Setup (Recommended)

KB-Admin has its own `docker-compose.yml` and runs as an independent microservice on the `laravel-microservices` network.

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key

# 2. Start service
docker-compose up -d

# 3. Run migrations
docker exec -it kb-admin python migrations/run_migrations.py

# 4. Access API docs
# Open http://localhost:8002/docs
```

See **[DOCKER_SETUP.md](DOCKER_SETUP.md)** for detailed Docker configuration and troubleshooting.

### Manual Setup (Development)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 3. Run migrations
python migrations/run_migrations.py

# 4. Start service
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints (Planned)

### Knowledge Base Management
- `POST /api/kb/create` - Create KB for agent
- `GET /api/kb/agent/{agent_type}` - Get active KB for agent
- `PUT /api/kb/{kb_id}/activate` - Activate KB
- `DELETE /api/kb/{kb_id}` - Delete KB

### Document Management
- `POST /api/kb/{kb_id}/documents/upload` - Upload document
- `POST /api/kb/{kb_id}/vectorize` - Trigger vectorization
- `GET /api/kb/{kb_id}/status` - Get vectorization status

### Self-Learning
- `POST /api/learning/capture/qa` - Capture Q&A pair
- `POST /api/learning/capture/solution` - Capture solution
- `GET /api/learning/queue` - Get pending review queue
- `POST /api/learning/{learned_id}/approve` - Approve and vectorize

## Integration with Idea-Agent

The idea-agent will use agent-specific KBs via minimal configuration changes:

```python
# In rag_tool.py
def get_vector_store(agent_type: str = "default"):
    index_name = f"kb_{agent_type}"  # Dynamic index selection
    return Redis(redis_url=redis_url, embedding=embeddings, index_name=index_name)
```

**No changes to agent logic** - agent_type flows through configuration.

## Development Status

### ✅ Completed (Phase 1 - Partial)
- FastAPI project structure
- Database connection with pooling
- Redis client with index management
- SQL migrations for all 4 tables
- Pydantic models for KB and documents
- Redis index management service
- Embedding service (OpenAI + Anthropic placeholder)
- Chunking service (with markdown support)

### 🚧 In Progress
- API routes implementation
- Vectorization service (chunking + embedding + storage)
- KB service (CRUD operations)

### 📋 TODO
- Complete API endpoints
- Document upload handler
- Vectorization worker
- Self-learning capture endpoints
- Admin portal (React UI)
- Docker Compose integration
- Tests

## Next Steps

1. Implement KB service (CRUD operations)
2. Implement vectorization service
3. Create API routes
4. Add to docker-compose.yml
5. Test KB creation and document vectorization
6. Integrate with idea-agent (Phase 2)

## License

Proprietary - Part of Laravel Developer Project
