# Phase 2 Complete - Agent Integration Testing Guide

## ✅ What Was Changed

**Phase 2 implemented minimal configuration-driven changes** to enable agents to use agent-specific knowledge bases:

### Files Modified (Total: ~35 lines)

1. **`idea-agent/app/tools/rag_tool.py`** (~15 lines)
   - Added `agent_type` parameter to `get_vector_store()`
   - Added `agent_type` parameter to `search_knowledge_base()` tool
   - Dynamic index selection: `kb_{agent_type}`
   - Backward compatible with default index

2. **`idea-agent/app/graph.py`** (~10 lines)
   - Added import for `search_knowledge_base`
   - Injected `agent_type="requirement_agent"` in `requirement_node()`
   - Updated `tool_node()` to inject `agent_type` into search calls

3. **`idea-agent/app/agents/requirement_agent.py`** (~5 lines)
   - Added `agent_type` parameter with default value
   - Added docstring

4. **`idea-agent/app/agents/developer_agent.py`** (~5 lines)
   - Added `agent_type` parameter with default value
   - Added docstring

**All changes are configuration-driven** - no logic changes to agent behavior!

---

## 🎯 How It Works Now

### Before Phase 2:
```
Agent → search_knowledge_base(query) → Redis index: "laravel_docs"
```

### After Phase 2:
```
requirement_agent → search_knowledge_base(query, agent_type="requirement_agent")
                 → Redis index: "kb_requirement_agent"

developer_agent → search_knowledge_base(query, agent_type="developer_agent")
               → Redis index: "kb_developer_agent"
```

**Key Point**: The `agent_type` is **automatically injected** from the graph state - agents don't need to know about it!

---

## 🧪 End-to-End Testing

### Prerequisites

1. **Services Running**:
   ```bash
   # Terminal 1: idea-agent (includes Redis)
   cd idea-agent
   docker-compose up -d

   # Terminal 2: kb-admin
   cd kb-admin
   docker-compose up -d

   # Check all services
   docker ps
   ```

2. **Migrations Run**:
   ```bash
   docker exec -it kb-admin python migrations/run_migrations.py
   ```

3. **API Key**: Add OpenAI API key to kb-admin `.env`

---

## Test Scenario 1: Create KB for Requirement Agent

### Step 1: Create Knowledge Base

```bash
curl -X POST http://localhost:8002/api/kb/create \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "requirement_agent",
    "name": "Requirement Agent KB - Laravel Best Practices",
    "description": "Knowledge base for requirement gathering",
    "embedding_provider": "openai",
    "chunk_size": 1000,
    "chunk_overlap": 200
  }'
```

**Expected Response**:
```json
{
  "id": 1,
  "agent_type": "requirement_agent",
  "name": "Requirement Agent KB - Laravel Best Practices",
  "status": "draft",
  "index_name": "kb_requirement_agent",
  "document_count": 0,
  "vector_count": 0
}
```

### Step 2: Create Sample Document

Create file `requirement_knowledge.md`:
```markdown
# Requirement Gathering Best Practices

## Business Context Stage
When gathering business context, always ask:
1. What problem does this solve?
2. Who are the target users?
3. What are the success metrics?
4. What is the budget and timeline?

## User Stories Stage
User stories should follow the format:
- As a [role]
- I want [feature]
- So that [benefit]

Always include acceptance criteria for each user story.

## Functional Requirements
Functional requirements must be:
- Specific and measurable
- Testable
- Complete
- Prioritized (Must have, Should have, Could have, Won't have)
```

### Step 3: Upload Document

```bash
curl -X POST http://localhost:8002/api/kb/1/documents/upload \
  -F "file=@requirement_knowledge.md" \
  -F "title=Requirement Gathering Best Practices"
```

**Expected Response**:
```json
{
  "document_id": 1,
  "title": "Requirement Gathering Best Practices",
  "status": "pending",
  "chunk_count": 0,
  "message": "Document uploaded successfully. Use /vectorize to process."
}
```

### Step 4: Vectorize Documents

```bash
curl -X POST http://localhost:8002/api/kb/1/vectorize \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Response**:
```json
{
  "job_id": "...",
  "status": "completed",
  "total_documents": 1,
  "message": "Processed 1 documents, 0 failed"
}
```

### Step 5: Activate KB

```bash
curl -X PUT http://localhost:8002/api/kb/1/activate
```

**Expected Response**:
```json
{
  "id": 1,
  "status": "active",
  "document_count": 1,
  "vector_count": 3
}
```

### Step 6: Verify in Redis

```bash
# Connect to Redis
docker exec -it redis-vector-db redis-cli

# List indexes
FT._LIST
# Should show: kb_requirement_agent

# Get index info
FT.INFO kb_requirement_agent
# Should show number of documents

# Search for content
FT.SEARCH kb_requirement_agent "user stories" LIMIT 0 5
# Should return relevant chunks
```

---

## Test Scenario 2: Test Agent Using KB

### Option A: Direct Test (Python)

Create `test_agent_kb.py` in idea-agent directory:

```python
from app.graph import app_graph
from langchain_core.messages import HumanMessage

# Configuration
config = {
    "configurable": {
        "thread_id": "test-123",
        "user_id": 2,
        "ai_provider": "OpenAI",  # or "Anthropic"
        "ai_api_key": "your-api-key-here"
    }
}

# Test question that should trigger KB search
inputs = {
    "messages": [
        HumanMessage(content="What should I include when gathering user stories?")
    ]
}

# Invoke agent
result = app_graph.invoke(inputs, config=config)

# Print response
last_message = result['messages'][-1]
print("Agent Response:")
print(last_message.content)
```

Run:
```bash
docker exec -it idea-agent python test_agent_kb.py
```

**Expected**: The agent should mention "As a [role], I want [feature], So that [benefit]" format from the KB!

### Option B: Via API (Full Integration)

```bash
# Start a conversation
curl -X POST http://localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the best practices for gathering user stories in requirements?",
    "user_id": 2,
    "ai_provider": "OpenAI",
    "ai_api_key": "your-openai-key"
  }'
```

**Look for**: Response should reference the format from the KB document!

---

## Test Scenario 3: Create KB for Developer Agent

### Step 1: Create Developer Agent KB

```bash
curl -X POST http://localhost:8002/api/kb/create \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "developer_agent",
    "name": "Developer Agent KB - Laravel Packages",
    "description": "Laravel packages and technical solutions",
    "embedding_provider": "openai"
  }'
```

### Step 2: Add Technical Knowledge

Create `laravel_auth.md`:
```markdown
# Laravel Authentication Solutions

## Laravel Sanctum
**Best for**: SPA authentication, mobile apps
**Features**:
- Lightweight token-based auth
- Perfect for Vue/React SPAs
- Built-in CSRF protection
- Simple API token management

**When to use**: Building a SPA or mobile app API

## Laravel Passport
**Best for**: OAuth2 server implementation
**Features**:
- Full OAuth2 server
- Perfect for third-party integrations
- Multiple grant types
- JWT tokens

**When to use**: Building an OAuth2 provider or complex API with third-party access

## Laravel Fortify
**Best for**: Headless authentication backend
**Features**:
- Frontend agnostic
- All auth features without views
- Works with any frontend framework

**When to use**: Custom frontend or mobile app with standard Laravel auth features
```

Upload and vectorize:
```bash
# Upload
curl -X POST http://localhost:8002/api/kb/2/documents/upload \
  -F "file=@laravel_auth.md"

# Vectorize
curl -X POST http://localhost:8002/api/kb/2/vectorize

# Activate
curl -X PUT http://localhost:8002/api/kb/2/activate
```

### Step 3: Test Developer Agent

The developer agent would be tested via the `/publish` endpoint which uses it to generate technical solutions.

---

## Verification Checklist

### ✅ KB-Admin Service
- [ ] KB created successfully
- [ ] Documents uploaded
- [ ] Vectorization completed
- [ ] Redis index exists (`FT._LIST` shows `kb_requirement_agent`)
- [ ] Vectors stored (`FT.INFO kb_requirement_agent` shows docs)
- [ ] KB activated (status = "active")

### ✅ Agent Integration
- [ ] Agent receives questions
- [ ] Agent calls `search_knowledge_base` tool when needed
- [ ] Tool receives correct `agent_type` parameter
- [ ] Correct Redis index queried (`kb_requirement_agent` for requirement agent)
- [ ] Relevant results returned from KB
- [ ] Agent incorporates KB knowledge in responses

### ✅ Backward Compatibility
- [ ] Old behavior works (without KB, falls back to "laravel_docs" index)
- [ ] No errors in logs
- [ ] All existing functionality intact

---

## Debugging

### Check Agent Type Injection

Add debug logging to `graph.py`:

```python
def requirement_node(state: AgentState, config: RunnableConfig):
    agent_type = "requirement_agent"
    print(f"DEBUG: Creating agent with type: {agent_type}")  # Add this
    # ... rest of code
```

### Check Tool Invocation

Add debug to `tool_node`:

```python
elif tool_name == 'search_knowledge_base':
    tool_args['agent_type'] = current_agent
    print(f"DEBUG: Searching KB with agent_type: {current_agent}")  # Add this
    result = search_knowledge_base.invoke(tool_args)
```

### Check Redis Index Selection

Add debug to `rag_tool.py`:

```python
def get_vector_store(agent_type: str = "default"):
    # ... existing code ...
    if agent_type and agent_type != "default":
        index_name = f"kb_{agent_type}"
    else:
        index_name = "laravel_docs"

    print(f"DEBUG: Using Redis index: {index_name}")  # Add this
    # ... rest of code
```

### Check Logs

```bash
# idea-agent logs
docker-compose logs -f idea-agent

# kb-admin logs
docker-compose logs -f kb-admin

# Redis logs
docker-compose logs redis-vector-db
```

---

## Common Issues

### Issue: Agent doesn't use KB

**Symptoms**: Agent responds but doesn't search KB

**Diagnosis**:
```bash
# Check if KB is active
curl http://localhost:8002/api/kb/agent/requirement_agent

# Should return status: "active"
```

**Solution**: Make sure KB status is "active", not "draft"

### Issue: search_knowledge_base returns error

**Symptoms**: Tool call fails

**Diagnosis**:
```bash
# Check Redis index exists
docker exec -it redis-vector-db redis-cli FT._LIST

# Should include: kb_requirement_agent
```

**Solution**: Run vectorization if index doesn't exist

### Issue: Empty results from KB

**Symptoms**: Tool succeeds but returns no results

**Diagnosis**:
```bash
# Check vector count
docker exec -it redis-vector-db redis-cli FT.INFO kb_requirement_agent

# Look for: num_docs > 0
```

**Solution**: Upload and vectorize documents

---

## Success Criteria

✅ **Phase 2 is successful when**:

1. KB created for requirement_agent via kb-admin API
2. Documents uploaded and vectorized
3. Redis index `kb_requirement_agent` contains vectors
4. Agent conversation triggers KB search
5. Agent response includes knowledge from uploaded documents
6. Different agent types use different indexes

---

## Next Steps After Testing

Once Phase 2 testing is complete:

1. **Create KBs for both agents** (requirement + developer)
2. **Upload comprehensive knowledge** (Laravel docs, best practices)
3. **Move to Phase 3**: Self-learning system to auto-capture Q&A
4. **Move to Phase 4**: Build admin portal UI

---

## Summary

**Phase 2 Changes**: ~35 lines of configuration code
**Testing Time**: ~30 minutes for full end-to-end
**Result**: Agents now use agent-specific knowledge bases automatically!

🎉 **When tests pass, Phase 2 is complete!**
