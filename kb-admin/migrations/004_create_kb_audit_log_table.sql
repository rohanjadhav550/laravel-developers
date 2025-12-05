-- KB Audit Log Table
CREATE TABLE IF NOT EXISTS kb_audit_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    kb_id BIGINT NOT NULL,
    action ENUM('created', 'updated', 'vectorized', 'activated', 'archived', 'document_added', 'document_removed') NOT NULL,
    user_id BIGINT,
    details JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (kb_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    KEY idx_kb_id (kb_id),
    KEY idx_action (action),
    KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
