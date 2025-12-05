-- Learned Knowledge Table
CREATE TABLE IF NOT EXISTS learned_knowledge (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    agent_type ENUM('requirement_agent', 'developer_agent', 'generic') NOT NULL,
    knowledge_type ENUM('qa_pair', 'solution_pattern', 'user_correction', 'context_pattern') NOT NULL,
    source_thread_id VARCHAR(255),
    source_conversation_id BIGINT,
    question TEXT,
    answer TEXT,
    context JSON,
    confidence_score DECIMAL(3,2) DEFAULT 0.00,
    status ENUM('pending_review', 'approved', 'rejected') DEFAULT 'pending_review',
    reviewed_by BIGINT NULL,
    reviewed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    KEY idx_agent_type (agent_type),
    KEY idx_status (status),
    KEY idx_knowledge_type (knowledge_type),
    KEY idx_source_thread (source_thread_id),
    KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
