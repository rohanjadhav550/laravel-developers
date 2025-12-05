-- Knowledge Bases Table
CREATE TABLE IF NOT EXISTS knowledge_bases (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    agent_type ENUM('requirement_agent', 'developer_agent', 'generic') NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status ENUM('draft', 'active', 'archived') DEFAULT 'draft',
    index_name VARCHAR(100) NOT NULL UNIQUE,
    embedding_provider ENUM('openai', 'anthropic') DEFAULT 'openai',
    embedding_model VARCHAR(100) DEFAULT 'text-embedding-3-small',
    chunk_size INT DEFAULT 1000,
    chunk_overlap INT DEFAULT 200,
    created_by BIGINT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_vectorized_at TIMESTAMP NULL,
    document_count INT DEFAULT 0,
    vector_count INT DEFAULT 0,

    KEY idx_agent_type (agent_type),
    KEY idx_status (status),
    UNIQUE KEY unique_agent_kb (agent_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
