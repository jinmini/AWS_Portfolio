-- ==========================================
-- Jinmini Portfolio Database Initialization
-- ==========================================

-- Create database (이미 docker-compose에서 생성됨)
-- CREATE DATABASE IF NOT EXISTS jinmini_portfolio;

-- ==========================================
-- AUTH SERVICE TABLES
-- ==========================================

-- 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 사용자 업데이트 트리거
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- BLOG SERVICE TABLES  
-- ==========================================

-- 카테고리 테이블
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 태그 테이블
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    slug VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 게시글 테이블
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    slug VARCHAR(255) UNIQUE NOT NULL,
    post_type VARCHAR(20) NOT NULL CHECK (post_type IN ('DEV', 'ESG')),
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    author_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    is_published BOOLEAN DEFAULT false,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 게시글 업데이트 트리거
CREATE TRIGGER update_posts_updated_at 
    BEFORE UPDATE ON posts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 게시글-태그 중간 테이블 (다대다 관계)
CREATE TABLE IF NOT EXISTS post_tags (
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)
);

-- 댓글 테이블
CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    author_name VARCHAR(100) NOT NULL,
    author_email VARCHAR(255),
    content TEXT NOT NULL,
    is_approved BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 기본 데이터 삽입
-- ==========================================

-- 관리자 사용자 생성 (비밀번호: admin123)
INSERT INTO users (email, password_hash, full_name, is_active, is_admin) 
VALUES (
    'admin@jinmini.com', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewvhRGwvZOI.5Q6e', -- admin123 해시
    'Jinmini Admin',
    true,
    true
) ON CONFLICT (email) DO NOTHING;

-- 기본 카테고리 생성
INSERT INTO categories (name, slug, description) VALUES 
    ('Development', 'development', '웹 개발, 프로그래밍 관련 포스트'),
    ('Frontend', 'frontend', '프론트엔드 개발 기술'),
    ('Backend', 'backend', '백엔드 개발 기술'),
    ('DevOps', 'devops', 'DevOps, 배포, 인프라 관련'),
    ('ESG', 'esg', 'ESG 컨설팅, 지속가능성 관련'),
    ('Career', 'career', '커리어, 성장 관련')
ON CONFLICT (slug) DO NOTHING;

-- 기본 태그 생성
INSERT INTO tags (name, slug) VALUES 
    ('React', 'react'),
    ('Next.js', 'nextjs'),
    ('TypeScript', 'typescript'),
    ('FastAPI', 'fastapi'),
    ('Python', 'python'),
    ('Docker', 'docker'),
    ('AWS', 'aws'),
    ('ESG', 'esg'),
    ('Sustainability', 'sustainability'),
    ('Career', 'career')
ON CONFLICT (slug) DO NOTHING;

-- 샘플 게시글 생성
INSERT INTO posts (title, content, summary, slug, post_type, category_id, author_id, is_published) VALUES 
    (
        'FastAPI로 마이크로서비스 구축하기',
        '# FastAPI 마이크로서비스 아키텍처

FastAPI는 현대적인 웹 API를 구축하는 데 최적화된 Python 프레임워크입니다...

## 주요 특징
- 높은 성능
- 자동 문서화
- 타입 힌팅 지원

## 구현 예시
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```',
        'FastAPI를 사용한 마이크로서비스 아키텍처 구축 가이드',
        'fastapi-microservice-guide',
        'DEV',
        2, -- Backend 카테고리
        1, -- Admin 사용자
        true
    ),
    (
        'ESG 경영의 미래와 기업의 대응 전략',
        '# ESG 경영의 중요성

ESG(Environmental, Social, Governance)는 현대 기업 경영의 핵심 지표가 되었습니다...

## 환경(Environmental)
- 탄소 중립 목표
- 재생 에너지 활용
- 순환 경제 모델

## 사회(Social)  
- 다양성과 포용성
- 직원 복지
- 지역사회 기여

## 지배구조(Governance)
- 투명한 경영
- 이사회 독립성
- 리스크 관리',
        'ESG 경영 트렌드와 기업의 실전 대응 방안',
        'esg-management-future-strategy',
        'ESG',
        5, -- ESG 카테고리
        1, -- Admin 사용자
        true
    )
ON CONFLICT (slug) DO NOTHING;

-- 게시글-태그 연결
INSERT INTO post_tags (post_id, tag_id) VALUES 
    (1, 4), -- FastAPI 포스트에 FastAPI 태그
    (1, 5), -- FastAPI 포스트에 Python 태그
    (1, 6), -- FastAPI 포스트에 Docker 태그
    (2, 8), -- ESG 포스트에 ESG 태그
    (2, 9)  -- ESG 포스트에 Sustainability 태그
ON CONFLICT DO NOTHING;

-- 샘플 댓글 생성
INSERT INTO comments (post_id, author_name, author_email, content, is_approved) VALUES 
    (1, '개발자김', 'dev.kim@example.com', 'FastAPI 정말 좋은 프레임워크네요! 실제 프로젝트에 적용해보고 싶습니다.', true),
    (2, 'ESG전문가', 'esg.expert@example.com', 'ESG 경영에 대한 인사이트가 정말 유용합니다. 감사합니다!', true)
ON CONFLICT DO NOTHING;

-- ==========================================
-- 인덱스 생성 (성능 최적화)
-- ==========================================

-- 게시글 검색용 인덱스
CREATE INDEX IF NOT EXISTS idx_posts_post_type ON posts(post_type);
CREATE INDEX IF NOT EXISTS idx_posts_is_published ON posts(is_published);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_category_id ON posts(category_id);

-- 댓글 검색용 인덱스
CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id);
CREATE INDEX IF NOT EXISTS idx_comments_is_approved ON comments(is_approved);

-- 사용자 검색용 인덱스  
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- ==========================================
-- 완료 메시지
-- ==========================================
DO $$
BEGIN
    RAISE NOTICE '✅ Database initialization completed successfully!';
    RAISE NOTICE '👤 Admin user: admin@jinmini.com (password: admin123)';
    RAISE NOTICE '📝 Sample posts and categories created';
END
$$; 