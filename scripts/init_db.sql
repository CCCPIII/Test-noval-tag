-- ============================================
-- AI小说总结与标签生成系统 - 数据库初始化脚本
-- ============================================

CREATE DATABASE IF NOT EXISTS novel_tag_db
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE novel_tag_db;

-- --------------------------------------------
-- 小说表
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS novels (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    title           VARCHAR(500)    NOT NULL COMMENT '小说名称',
    author          VARCHAR(200)    NULL COMMENT '作者',
    file_path       VARCHAR(1000)   NULL COMMENT '文件存储路径',
    file_hash       VARCHAR(64)     NULL UNIQUE COMMENT '文件SHA-256哈希（用于去重）',
    file_size       BIGINT          NULL COMMENT '文件大小（字节）',
    char_count      BIGINT          DEFAULT 0 COMMENT '小说字数',
    status          VARCHAR(20)     DEFAULT 'uploaded' COMMENT '状态: uploaded/processing/done/error',
    upload_time     DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    updated_at      DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_title (title(100)),
    INDEX idx_status (status),
    INDEX idx_upload_time (upload_time)
) ENGINE=InnoDB COMMENT='小说信息表';

-- --------------------------------------------
-- 总结表
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS summaries (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    novel_id        INT             NOT NULL COMMENT '关联小说ID',
    content         TEXT            NOT NULL COMMENT '总结内容',
    target_length   INT             NULL COMMENT '目标总结长度',
    actual_length   INT             NULL COMMENT '实际总结长度',
    model_used      VARCHAR(100)    NULL COMMENT '使用的AI模型',
    is_chunk_summary TINYINT(1)     DEFAULT 0 COMMENT '是否为分段总结',
    chunk_index     INT             NULL COMMENT '分段序号',
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_novel_id (novel_id),
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='小说总结表';

-- --------------------------------------------
-- 标签表
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS tags (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100)    NOT NULL COMMENT '标签名称',
    dimension       VARCHAR(20)     NOT NULL COMMENT '标签维度: genre/style/element/character/exclusive',
    is_custom       TINYINT(1)      DEFAULT 0 COMMENT '是否为自定义标签',
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_name_dimension (name, dimension),
    INDEX idx_dimension (dimension)
) ENGINE=InnoDB COMMENT='标签表';

-- --------------------------------------------
-- 小说-标签关联表
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS novel_tags (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    novel_id        INT             NOT NULL COMMENT '小说ID',
    tag_id          INT             NOT NULL COMMENT '标签ID',
    confidence      FLOAT           NULL COMMENT 'AI生成的置信度',
    is_manual       TINYINT(1)      DEFAULT 0 COMMENT '是否手动添加',
    is_controversial TINYINT(1)     DEFAULT 0 COMMENT '是否为争议标签',
    controversy_note VARCHAR(200)   NULL COMMENT '争议标签解释（50字以内）',
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_novel_tag (novel_id, tag_id),
    INDEX idx_novel_id (novel_id),
    INDEX idx_tag_id (tag_id),
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='小说-标签关联表';

-- --------------------------------------------
-- 传统标签库表
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS tag_library (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100)    NOT NULL COMMENT '标签名称',
    dimension       VARCHAR(20)     NOT NULL COMMENT '标签维度',
    description     VARCHAR(500)    NULL COMMENT '标签描述',
    sort_order      INT             DEFAULT 0 COMMENT '排序序号',
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    UNIQUE KEY uk_name_dimension (name, dimension),
    INDEX idx_dimension (dimension)
) ENGINE=InnoDB COMMENT='传统标签库';

-- --------------------------------------------
-- AI模型配置表
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS ai_models (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100)    NOT NULL UNIQUE COMMENT '模型名称',
    provider        VARCHAR(50)     NOT NULL COMMENT '提供商: openai/zhipu/local/custom',
    api_url         VARCHAR(500)    NOT NULL COMMENT 'API接口地址',
    api_key_encrypted VARCHAR(500)  NULL COMMENT '加密后的API密钥',
    model_identifier VARCHAR(200)   NOT NULL COMMENT '模型标识符',
    is_active       TINYINT(1)      DEFAULT 1 COMMENT '是否启用',
    max_tokens      INT             DEFAULT 4096 COMMENT '最大token数',
    description     VARCHAR(1000)   NULL COMMENT '模型描述',
    supported_max_chars BIGINT      NULL COMMENT '支持的最大小说字数',
    avg_speed       VARCHAR(50)     NULL COMMENT '平均速度描述',
    accuracy_note   VARCHAR(200)    NULL COMMENT '准确率说明',
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_provider (provider),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB COMMENT='AI模型配置表';

-- --------------------------------------------
-- 用户表（预留）
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(100)    NOT NULL UNIQUE COMMENT '用户名',
    password_hash   VARCHAR(200)    NOT NULL COMMENT '密码哈希',
    email           VARCHAR(200)    NULL COMMENT '邮箱',
    is_active       TINYINT(1)      DEFAULT 1 COMMENT '是否启用',
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_username (username)
) ENGINE=InnoDB COMMENT='用户表（预留）';

-- --------------------------------------------
-- 用户收藏表（预留）
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS user_favorites (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT             NOT NULL COMMENT '用户ID',
    novel_id        INT             NOT NULL COMMENT '小说ID',
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
    UNIQUE KEY uk_user_novel (user_id, novel_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='用户收藏表（预留）';
