-- KB Documents Table
CREATE TABLE IF NOT EXISTS kb_documents (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    kb_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content LONGTEXT NOT NULL,
    source_type ENUM('upload', 'learned', 'manual', 'imported') DEFAULT 'upload',
    source_reference VARCHAR(255),
    metadata JSON,
    chunk_count INT DEFAULT 0,
    status ENUM('pending', 'vectorized', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (kb_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    KEY idx_kb_status (kb_id, status),
    KEY idx_source_type (source_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
