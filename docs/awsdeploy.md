# AWS 배포 가이드 - Jinmini Portfolio & Blog

## 📋 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [배포 전 준비사항](#배포-전-준비사항)
3. [AWS EC2 인스턴스 설정](#aws-ec2-인스턴스-설정)
4. [로컬 보안 설정 강화](#로컬-보안-설정-강화)
5. [EC2 서버 환경 구축](#ec2-서버-환경-구축)
6. [애플리케이션 배포](#애플리케이션-배포)
7. [서비스 상태 확인](#서비스-상태-확인)
8. [트러블슈팅](#트러블슈팅)
9. [성능 최적화](#성능-최적화)

---

## 🎯 프로젝트 개요

### 아키텍처
- **마이크로서비스 구조**: Auth Service, Blog Service, API Gateway
- **백엔드**: FastAPI + PostgreSQL + Redis
- **프론트엔드**: Next.js
- **컨테이너화**: Docker + Docker Compose
- **배포 환경**: AWS EC2 (Amazon Linux 2023)

### 서비스 포트 구성
- PostgreSQL: 5432
- Redis: 6379
- Auth Service: 8001
- Blog Service: 8002
- API Gateway: 8000
- Frontend: 3000

---

## 🔧 배포 전 준비사항

### 1. 로컬 개발 완료 확인
- [ ] 모든 서비스가 로컬에서 정상 동작
- [ ] Docker Compose로 전체 서비스 실행 가능
- [ ] API 엔드포인트 테스트 완료

### 2. 보안 설정 체크리스트
- [ ] JWT_SECRET_KEY 생성 및 설정
- [ ] 강력한 데이터베이스 비밀번호 설정
- [ ] .env 파일이 .gitignore에 포함되어 있는지 확인
- [ ] 프로덕션용 docker-compose.prod.yml 준비

### 3. AWS 계정 및 권한
- [ ] AWS 계정 생성/로그인
- [ ] EC2 사용 권한 확인
- [ ] 키 페어 생성 준비

---

## 🏗️ AWS EC2 인스턴스 설정

### 1. EC2 인스턴스 생성

#### 인스턴스 구성
```
AMI: Amazon Linux 2023
인스턴스 타입: t2.micro (프리티어)
키 페어: 새로 생성 또는 기존 키 사용
스토리지: 8GB (기본값)
```

#### 보안 그룹 설정
```
인바운드 규칙:
- SSH (22): 내 IP만 허용
- HTTP (80): 0.0.0.0/0
- HTTPS (443): 0.0.0.0/0
- 사용자 정의 TCP (3000): 내 IP만 허용 (프론트엔드)
- 사용자 정의 TCP (8080): 내 IP만 허용 (API Gateway)
- 사용자 정의 TCP (8101): 내 IP만 허용 (Auth Service)
- 사용자 정의 TCP (8102): 내 IP만 허용 (Blog Service)

⚠️ 개발/테스트 환경에서는 모든 TCP (0-65535)를 내 IP로 제한하여 사용 가능
⚠️ 실제 사용 포트: 3000, 8080, 8101, 8102
```

### 2. SSH 접속 설정
```bash
# Windows (PowerShell)
ssh -i "your-key.pem" ec2-user@your-ec2-public-ip

# 권한 오류 시 (Windows)
icacls "your-key.pem" /inheritance:r /grant:r "%username%:(R)"
```

#### 🚨 외부 접속 불가 문제 해결 (가장 일반적인 문제)

**1단계: AWS 콘솔에서 보안 그룹 확인**
```
1. AWS EC2 콘솔 접속
2. 인스턴스 선택 → 보안 탭 → 보안 그룹 클릭
3. 인바운드 규칙 확인
4. 필요한 포트가 열려있는지 확인:
   - 3000 (프론트엔드)
   - 8080 (API Gateway)
   - 8101 (Auth Service) - 선택사항
   - 8102 (Blog Service) - 선택사항
```

**2단계: 보안 그룹 수정**
```
인바운드 규칙 편집:
- 유형: 사용자 정의 TCP
- 포트 범위: 3000
- 소스: 내 IP (또는 0.0.0.0/0 - 테스트용)

- 유형: 사용자 정의 TCP  
- 포트 범위: 8080
- 소스: 내 IP (또는 0.0.0.0/0 - 테스트용)
```

**3단계: 즉시 테스트**
```bash
# 브라우저에서 접속 테스트
http://your-ec2-ip:3000
http://your-ec2-ip:8080/docs
```

---

## 🔐 로컬 보안 설정 강화

### 1. JWT Secret Key 생성
```bash
# Python으로 안전한 키 생성
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. 데이터베이스 비밀번호 생성
```bash
# 강력한 비밀번호 생성
python -c "import secrets; import string; chars = string.ascii_letters + string.digits; print(''.join(secrets.choice(chars) for i in range(16)))"
```

### 3. 환경변수 설정
```env
# .env 파일 예시
JWT_SECRET_KEY=your_generated_jwt_secret
POSTGRES_PASSWORD=your_strong_password
POSTGRES_USER=jinmini
POSTGRES_DB=jinmini_blog
REDIS_URL=redis://redis:6379
```

### 4. 프로덕션 Docker Compose 준비
```yaml
# docker-compose.prod.yml 생성
version: '3.8'
services:
  # 프로덕션 환경에 맞는 설정
  # 환경변수는 별도 파일로 관리
```

### 5. .gitignore 확인
```gitignore
# 중요 파일들이 포함되었는지 확인
.env
.env.*
*.pem
aws/
.aws/
```

---

## 🖥️ EC2 서버 환경 구축

### 1. 시스템 업데이트
```bash
sudo dnf update -y
```

### 2. Docker 설치
```bash
# Docker 설치
sudo dnf install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# 로그아웃 후 재로그인 또는
newgrp docker

# Docker 설치 확인
docker --version
```

### 3. Docker Compose 설치
```bash
# Docker Compose 최신 버전 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Docker Compose 설치 확인
docker-compose --version
```

### 4. Git 설치 및 프로젝트 클론
```bash
# Git 설치 (보통 기본 설치됨)
sudo dnf install -y git

# 프로젝트 클론
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

---

## 🚀 애플리케이션 배포

### 1. 환경변수 설정
```bash
# .env 파일 생성 및 편집
nano .env

# 또는 직접 입력
cat > .env << EOF
JWT_SECRET_KEY=your_jwt_secret_here
POSTGRES_PASSWORD=your_db_password_here
POSTGRES_USER=jinmini
POSTGRES_DB=jinmini_blog
REDIS_URL=redis://redis:6379
EOF
```

### 2. Docker 이미지 빌드 및 서비스 시작
```bash
# 백그라운드에서 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 3. 서비스별 시작 순서 (문제 발생 시)
```bash
# 1단계: 인프라 서비스 먼저
docker-compose up -d postgres redis

# 2단계: 백엔드 서비스
docker-compose up -d auth-service blog-service

# 3단계: API Gateway
docker-compose up -d api-gateway

# 4단계: 프론트엔드 (가장 시간이 오래 걸림)
docker-compose up -d frontend
```

---

## ✅ 서비스 상태 확인

### 1. 컨테이너 상태 확인
```bash
# 모든 컨테이너 상태 확인
docker-compose ps

# 특정 서비스 로그 확인
docker-compose logs service-name

# 실시간 로그 확인
docker-compose logs -f service-name
```

### 2. API 엔드포인트 테스트
```bash
# API Gateway 헬스체크
curl http://localhost:8000/health

# 블로그 서비스 테스트
curl http://localhost:8000/api/v1/blogs/

# Auth 서비스 테스트
curl http://localhost:8000/api/v1/auth/health
```

### 3. 데이터베이스 확인
```bash
# PostgreSQL 컨테이너 접속
docker-compose exec postgres psql -U jinmini -d jinmini_blog

# 테이블 확인
\dt

# 샘플 데이터 확인
SELECT * FROM blog_posts LIMIT 5;
```

### 4. 외부 접속 테스트
```bash
# 브라우저 또는 curl로 테스트
# http://your-ec2-public-ip:8000/health
# http://your-ec2-public-ip:3000 (프론트엔드)
```

---

## 🔧 트러블슈팅

### 1. 일반적인 문제들

#### Docker 권한 오류
```bash
# 증상: permission denied while trying to connect to Docker daemon
# 해결: 사용자를 docker 그룹에 추가
sudo usermod -a -G docker $USER
newgrp docker
```

#### 포트 충돌
```bash
# 증상: Port already in use
# 해결: 기존 프로세스 종료
sudo lsof -i :포트번호
sudo kill -9 PID
```

#### 메모리 부족 (t2.micro)
```bash
# 증상: 컨테이너가 자주 종료됨
# 해결: 스왑 메모리 생성
sudo dd if=/dev/zero of=/swapfile bs=1M count=1024
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 2. 서비스별 트러블슈팅

#### PostgreSQL 연결 실패
```bash
# 로그 확인
docker-compose logs postgres

# 컨테이너 재시작
docker-compose restart postgres

# 데이터베이스 초기화 (주의: 데이터 손실)
docker-compose down -v
docker-compose up -d postgres
```

#### Next.js 빌드 시간 지연
```bash
# 증상: 빌드가 10-20분 소요
# 원인: t2.micro의 제한된 리소스 (1GB RAM, 1 vCPU)
# 대안:
# 1. 로컬에서 빌드 후 이미지 푸시
# 2. 더 큰 인스턴스 타입 사용
# 3. CI/CD 파이프라인 구축
```

#### Redis 연결 오류
```bash
# Redis 상태 확인
docker-compose exec redis redis-cli ping

# 연결 테스트
docker-compose exec api-gateway ping redis
```

### 3. 로그 분석 방법
```bash
# 전체 서비스 로그
docker-compose logs

# 에러 로그만 필터링
docker-compose logs | grep -i error

# 특정 시간대 로그
docker-compose logs --since="2024-01-01T00:00:00"

# 실시간 로그 모니터링
docker-compose logs -f --tail=100
```

---

## ⚡ 성능 최적화

### 1. 메모리 최적화
```bash
# 스왑 메모리 설정 (t2.micro 권장)
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 영구 설정
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 2. Docker 리소스 제한
```yaml
# docker-compose.yml에 추가
services:
  frontend:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### 3. 빌드 최적화 전략
```bash
# 1. Multi-stage 빌드 사용
# 2. .dockerignore 최적화
# 3. 빌드 캐시 활용
# 4. 사전 빌드된 이미지 사용
```

---

## 📈 CI/CD 고려사항

### 1. GitHub Actions 활용
```yaml
# .github/workflows/deploy.yml 예시
# 로컬에서 빌드 후 Docker Hub에 푸시
# EC2에서 이미지 pull하여 배포
```

### 2. 배포 자동화
```bash
# 배포 스크립트 예시
#!/bin/bash
docker-compose pull
docker-compose up -d
docker-compose logs -f
```

### 3. 모니터링 설정
```bash
# 서비스 상태 모니터링
# 로그 수집 및 분석
# 알림 설정
```

---

## 📝 체크리스트

### 배포 완료 확인
- [ ] 모든 컨테이너가 정상 실행 중
- [ ] API 엔드포인트 응답 정상
- [ ] 데이터베이스 연결 및 데이터 확인
- [ ] 프론트엔드 접속 가능
- [ ] 외부 IP로 접속 가능
- [ ] 보안 그룹 설정 확인
- [ ] 로그 모니터링 설정

### 보안 확인
- [ ] 기본 비밀번호 변경 완료
- [ ] 불필요한 포트 차단
- [ ] SSH 키 안전하게 보관
- [ ] 환경변수 파일 gitignore 적용
- [ ] HTTPS 설정 (선택사항)

---

## 🆘 긴급 상황 대응

### 서비스 전체 중단
```bash
# 1. 즉시 중단
docker-compose down

# 2. 로그 확인
docker-compose logs > emergency_logs.txt

# 3. 백업에서 복구
git reset --hard HEAD
docker-compose up -d
```

### 데이터베이스 문제
```bash
# 1. 데이터베이스 백업
docker-compose exec postgres pg_dump -U jinmini jinmini_blog > backup.sql

# 2. 컨테이너 재생성
docker-compose down
docker volume rm $(docker volume ls -q)
docker-compose up -d
```

---

## 📞 추가 리소스

- [Docker 공식 문서](https://docs.docker.com/)
- [AWS EC2 사용자 가이드](https://docs.aws.amazon.com/ec2/)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/)
- [Next.js 배포 문서](https://nextjs.org/docs/deployment)

---

## 🎯 배포 전략 비교 (MVP vs Scale)

### MVP 단계 권장 배포 방식

#### **Option 1: 클라우드 플랫폼 조합** (가장 권장)
```
프론트엔드: Vercel
- Next.js에 최적화된 플랫폼
- 자동 CI/CD 및 배포
- 글로벌 CDN 지원
- 무료 티어로 충분

백엔드: Railway
- Docker 이미지 직접 배포
- PostgreSQL 호스팅 포함
- 간단한 환경변수 관리
- Redis 애드온 지원
```

#### **Option 2: Serverless 아키텍처**
```
프론트엔드: Vercel/Netlify
백엔드: Vercel Functions / AWS Lambda
데이터베이스: PlanetScale / Supabase
```

### 확장 단계 (서비스 성장 시)

#### **AWS 풀 스택 배포**
```
컴퓨팅: ECS Fargate / EKS
데이터베이스: RDS (Multi-AZ)
캐시: ElastiCache
로드밸런서: ALB
CDN: CloudFront
```

#### **성능 향상 포인트**
- **인스턴스 타입**: t3.small 이상 (2GB RAM, 2 vCPU)
- **관리형 서비스**: RDS, ElastiCache 사용
- **Auto Scaling**: 트래픽에 따른 자동 확장
- **모니터링**: CloudWatch, 알람 설정

### 비용 비교 (월 예상 비용)

#### **MVP 단계**
```
Vercel (프론트엔드): $0 (Pro: $20)
Railway (백엔드): $5-20
총 비용: $5-40/월
```

#### **AWS 확장 단계**
```
ECS (t3.small): $15-30
RDS (t3.micro): $15-25
기타 서비스: $10-20
총 비용: $40-75/월
```

### 배포 방식 선택 기준

#### **MVP/개인 프로젝트** → **클라우드 플랫폼 조합**
- ✅ 빠른 배포
- ✅ 관리 부담 최소
- ✅ 낮은 비용
- ✅ 자동 CI/CD

#### **프로덕션/팀 프로젝트** → **AWS 풀 스택**
- ✅ 완전한 제어권
- ✅ 높은 성능
- ✅ 확장성
- ✅ 엔터프라이즈 기능

---

## 💡 학습 성과 및 다음 단계

### 이번 프로젝트에서 습득한 핵심 역량
- [x] **AWS 인프라 구축**: EC2, 보안 그룹, 네트워킹
- [x] **Docker 컨테이너화**: 마이크로서비스 아키텍처
- [x] **보안 설정**: JWT, 환경변수, 패스워드 관리
- [x] **트러블슈팅**: 체계적인 문제 분석 및 해결
- [x] **성능 최적화**: 리소스 제약 환경에서의 최적화
- [x] **배포 전략**: 다양한 배포 옵션의 장단점 이해

### 실무 적용 가능한 지식
```
1. DevOps 파이프라인 설계 능력
2. 클라우드 인프라 구축 경험
3. 마이크로서비스 배포 노하우
4. 비용 효율적인 배포 전략 수립
5. 문제 해결 및 디버깅 역량
```

### 다음 학습 방향
- **CI/CD 파이프라인**: GitHub Actions, Jenkins
- **모니터링**: Prometheus, Grafana, ELK Stack
- **보안 강화**: HTTPS, WAF, 취약점 스캔
- **성능 튜닝**: 캐싱 전략, DB 최적화
- **인프라 자동화**: Terraform, CloudFormation

---

**결론**: MVP 단계에서는 **Vercel + Railway** 조합이 가장 현실적이며, 서비스가 성장할 때 AWS로 마이그레이션하는 것이 효율적인 전략입니다.

**작성일**: 2025년 5월 30일
**작성자**: Jinmini
**프로젝트**: Jinmini Portfolio & Blog
**환경**: AWS EC2 + Docker + Microservices
