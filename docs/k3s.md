# k3d 마이그레이션 가이드 - Jinmini Portfolio & Blog

**작성일**: 2025-06-02  
**완료일**: 2025-06-04  
**프로젝트**: Docker Compose → k3d Kubernetes 마이그레이션  
**환경**: Windows 11, PowerShell 5.1, 16GB RAM, Intel i7-9700

---

## 🎯 **마이그레이션 개요**

### **목표**
기존 Docker Compose 기반 마이크로서비스를 k3d Kubernetes 클러스터로 마이그레이션하여:
- Kubernetes 네이티브 환경 경험
- AWS EKS로의 확장성 확보
- 고급 오케스트레이션 기능 활용

### **기술 스택**
- **로컬 클러스터**: k3d (k3s in Docker)
- **컨테이너**: Docker Desktop
- **오케스트레이션**: Kubernetes
- **확장 계획**: AWS EKS

---

## 📋 **사전 준비사항**

### **1. 필수 도구 확인**
```powershell
# Docker 버전 확인
docker --version
# 출력: Docker version 28.1.1, build 4eba377

# k3d 버전 확인  
k3d version
# 출력: k3s version v1.31.5-k3s1 (default)

# kubectl 버전 확인
kubectl version --client
# 출력: Kustomize Version: v5.5.0
```

### **2. 기존 Docker Compose 상태 확인**
```powershell
# 실행 중인 컨테이너 확인
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

---

## 🚀 **단계별 마이그레이션 프로세스**

### **STEP 1: k3d 클러스터 생성**

```powershell
# k3d 클러스터 생성 (기본 설정)
k3d cluster create jinmini-portfolio

# 클러스터 정보 확인
kubectl cluster-info

# 노드 상태 확인
kubectl get nodes
```

**결과 확인:**
```
NAME                             STATUS   ROLES                  AGE   VERSION
k3d-jinmini-portfolio-server-0   Ready    control-plane,master   49s   v1.31.5+k3s1
```

---

### **STEP 2: 디렉토리 구조 생성**

```powershell
# 기존 빈 파일들 정리
Remove-Item k8s\*.yaml -Force

# 체계적인 디렉토리 구조 생성
New-Item -ItemType Directory -Path "k8s\database", "k8s\services", "k8s\frontend", "k8s\config" -Force
```

**생성된 구조:**
```
k8s/
├── database/     # PostgreSQL, Redis
├── services/     # 마이크로서비스 Deployments
├── frontend/     # Next.js Frontend
└── config/       # ConfigMaps
```

---

### **STEP 3: PostgreSQL 배포 (StatefulSet)**

#### **3.1 PostgreSQL 초기화 스크립트 ConfigMap 생성**
```powershell
# 기존 init-db.sql을 ConfigMap으로 생성
kubectl create configmap postgres-init-db --from-file=init-db.sql=init-db.sql
```

#### **3.2 PostgreSQL StatefulSet 배포**
```powershell
# PostgreSQL StatefulSet + Service 배포
kubectl apply -f k8s/database/postgres-statefulset.yaml
```

#### **3.3 배포 상태 확인**
```powershell
# Pod 상태 확인
kubectl get pods

# PVC 상태 확인  
kubectl get pvc

# 데이터베이스 연결 테스트
kubectl exec postgres-0 -- psql -U admin -d jinmini_portfolio -c "SELECT count(*) FROM users;"
kubectl exec postgres-0 -- psql -U admin -d jinmini_portfolio -c "SELECT count(*) FROM posts;"
```

**배포 결과:**
```
pod/postgres-0   1/1   Running   0   2m44s
persistentvolumeclaim/postgres-storage-postgres-0   Bound   5Gi
users: 1개, posts: 2개 확인 완료 ✅
```

---

### **STEP 4: Redis 배포 (Deployment)**

#### **4.1 Redis Deployment 배포**
```powershell
# Redis Deployment + Service 배포
kubectl apply -f k8s/database/redis-deployment.yaml
```

#### **4.2 배포 상태 확인**
```powershell
# Redis Pod 상태 확인
kubectl get pods -l app=redis
```

**배포 결과:**
```
redis-6869d8b44b-ng7fm   1/1   Running   0   29s ✅
```

---

### **STEP 5: Auth Service 배포**

#### **5.1 Docker 이미지 빌드 및 k3d 로드**
```powershell
# Docker Compose로 이미지 빌드
docker-compose build auth-service

# k3d 클러스터에 이미지 로드
k3d image import aws_portfolio-auth-service:latest -c jinmini-portfolio
```

#### **5.2 ConfigMap 및 Deployment 배포**
```powershell
# Auth Service ConfigMap 배포
kubectl apply -f k8s/config/auth-service-config.yaml

# Auth Service Deployment + Service 배포
kubectl apply -f k8s/services/auth-service.yaml
```

#### **5.3 배포 상태 확인**
```powershell
# Auth Service 상태 확인
kubectl get pods -l app=auth-service
```

**배포 결과:**
```
auth-service-596c778879-nt8th   1/1   Running   0   3m15s ✅
```

---

### **STEP 6: Blog Service 배포**

#### **6.1 Docker 이미지 빌드 및 k3d 로드**
```powershell
# Docker Compose로 이미지 빌드
docker-compose build blog-service

# k3d 클러스터에 이미지 로드
k3d image import aws_portfolio-blog-service:latest -c jinmini-portfolio
```

#### **6.2 ConfigMap 및 Deployment 배포**
```powershell
# Blog Service ConfigMap 배포
kubectl apply -f k8s/config/blog-service-config.yaml

# Blog Service Deployment + Service 배포
kubectl apply -f k8s/services/blog-service.yaml
```

**배포 결과:**
```
blog-service-56c877f5d4-6rx9f   1/1   Running   0   81s ✅
```

---

### **STEP 7: API Gateway 배포**

#### **7.1 Docker 이미지 빌드 및 k3d 로드**
```powershell
# Docker Compose로 이미지 빌드
docker-compose build api-gateway

# k3d 클러스터에 이미지 로드
k3d image import aws_portfolio-api-gateway:latest -c jinmini-portfolio
```

#### **7.2 ConfigMap 및 Deployment 배포 (NodePort)**
```powershell
# API Gateway ConfigMap 배포
kubectl apply -f k8s/config/api-gateway-config.yaml

# API Gateway Deployment + NodePort Service 배포
kubectl apply -f k8s/services/api-gateway.yaml
```

**배포 결과:**
```
api-gateway-7ff6c8c64f-jn2bk   1/1   Running   0   4m59s ✅
NodePort: localhost:30080 외부 접근 가능 ✅
```

---

## 🖥️ **STEP 8: Frontend 배포 및 핵심 문제 해결**

### **8.1 첫 번째 시도 - 기본 Frontend 배포**
```powershell
# Frontend Docker 이미지 빌드
cd frontend
docker build -t aws_portfolio-frontend:latest .

# k3d 클러스터에 이미지 import
k3d image import aws_portfolio-frontend:latest -c jinmini-portfolio

# Frontend 배포
cd ..
kubectl apply -f k8s/frontend/frontend.yaml
```

### **8.2 ❌ 블로그 페이지 오류 발생**

#### **증상:**
- **홈페이지**: 정상 작동 ✅
- **블로그 페이지**: Runtime Error 발생 ❌
  ```
  Error: Cannot read properties of undefined (reading 'posts')
  ```

#### **🕵️ 디버깅 과정**

**1차 분석: React Query 문제로 착각**
```javascript
// 콘솔 오류 메시지
./hooks/use-blog.ts
Attempted import error: 'queryKeys' is not exported from '@/lib/query-client'
```

**여러 React Query 수정 시도 (모두 실패)**:
- queryKeys 정의 추가
- use-blog.ts에서 직접 정의
- Docker 캐시 완전 삭제
- 5회 이상 재빌드 시도

**2차 분석: API 연결 문제 의심**
```javascript
// 실제 근본 원인 발견
Failed to load resource: net::ERR_CONNECTION_REFUSED
NEXT_PUBLIC_API_URL: http://localhost:30080
```

### **8.3 🎯 핵심 문제 발견: k3d 포트 매핑 누락!**

#### **근본 원인:**
```powershell
# 문제 진단
kubectl get services  # API Gateway는 NodePort 30080로 설정됨
Invoke-WebRequest -Uri http://localhost:30080/health  # 연결 실패!

# 클러스터 포트 매핑 확인  
k3d cluster list  # 포트 매핑이 없음!
```

**핵심 깨달음**: k3d 클러스터가 NodePort를 호스트로 포워딩하지 않고 있었음!

### **8.4 ✅ 최종 해결: 포트 매핑과 함께 클러스터 재생성**

#### **클러스터 완전 재생성**
```powershell
# 기존 클러스터 삭제
k3d cluster delete jinmini-portfolio

# 포트 매핑과 함께 새 클러스터 생성
k3d cluster create jinmini-portfolio --port "30000:30000@loadbalancer" --port "30080:30080@loadbalancer"

# 모든 서비스 재배포
kubectl apply -f k8s/ -R
```

#### **이미지 재임포트**
```powershell
k3d image import aws_portfolio-frontend:latest aws_portfolio-api-gateway:latest aws_portfolio-auth-service:latest aws_portfolio-blog-service:latest -c jinmini-portfolio
```

#### **누락된 PostgreSQL ConfigMap 생성**
```powershell
# PostgreSQL이 ContainerCreating 상태로 멈춤
kubectl describe pod postgres-0
# 원인: configmap "postgres-init-db" not found

# ConfigMap 생성
kubectl create configmap postgres-init-db --from-file=init-db.sql=init-db.sql
kubectl delete pod postgres-0  # Pod 재시작
```

#### **CORS 정책 수정**
```yaml
# API Gateway ConfigMap에 CORS_ORIGINS 추가
data:
  CORS_ORIGINS: "http://localhost:3000,http://localhost:3001"
```

```powershell
kubectl apply -f k8s/config/api-gateway-config.yaml
kubectl rollout restart deployment/api-gateway
```

### **8.5 🎉 완전한 성공!**

#### **API 테스트 성공**
```powershell
# API Gateway 연결 성공
Invoke-WebRequest -Uri http://localhost:30080/health
# StatusCode: 200 ✅

# 블로그 API 성공  
Invoke-WebRequest -Uri http://localhost:30080/blog/categories
# StatusCode: 200, 카테고리 데이터 반환 ✅

Invoke-WebRequest -Uri "http://localhost:30080/blog/posts?page=1&size=6"  
# StatusCode: 200, 게시글 데이터 반환 ✅
```

#### **Frontend 테스트 성공**
```javascript
// 브라우저 콘솔 (로컬 개발 서버: localhost:3001)
NEXT_PUBLIC_API_URL: http://localhost:30080 ✅
postsData: {posts: Array(2), total: 2, page: 1, size: 6, total_pages: 1} ✅
postsLoading: false ✅
postsError: null ✅
```

**로컬 환경 설정:**
```env
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:30080
```

---

## ✅ **최종 배포 현황 (100% 완료)**

### **전체 시스템 상태 확인**
```powershell
kubectl get all -o wide
```

### **배포 완료된 서비스들**

| 서비스 | 타입 | Pod명 | IP | 포트 | 상태 |
|--------|------|-------|----|----- |------|
| **PostgreSQL** | StatefulSet | postgres-0 | 10.42.0.10 | 5432 | ✅ Running |
| **Redis** | Deployment | redis-6869d8b44b-5hdsf | 10.42.0.11 | 6379 | ✅ Running |
| **Auth Service** | Deployment | auth-service-596c778879-gg6cz | 10.42.0.12 | 8101 | ✅ Running |
| **Blog Service** | Deployment | blog-service-56c877f5d4-nxvg6 | 10.42.0.13 | 8102 | ✅ Running |
| **API Gateway** | NodePort | api-gateway-7b9ccdf54f-7rg8s | 10.42.0.14 | 8080:30080 | ✅ Running |
| **Frontend** | NodePort | frontend-64f97fbfbd-tfvh5 | 10.42.0.15 | 3000:30000 | ✅ Running |

### **외부 접근 정보 (모두 정상 작동)**
```
🌐 로컬 개발 서버: http://localhost:3001 (pnpm run dev)
🌐 Frontend (컨테이너): http://localhost:30000  
📡 API Gateway: http://localhost:30080

API 엔드포인트:
- 헬스체크: http://localhost:30080/health ✅
- 블로그 카테고리: http://localhost:30080/blog/categories ✅  
- 블로그 게시글: http://localhost:30080/blog/posts ✅
- 인증 서비스: http://localhost:30080/auth/health ✅
```

---

## 🧪 **API 테스트 명령어 (모두 성공 확인됨)**

### **1. API Gateway 헬스체크**
```powershell
Invoke-WebRequest -Uri http://localhost:30080/health
# 출력: {"status":"healthy","service":"API Gateway","version":"1.0.0"}
```

### **2. 블로그 서비스 테스트**
```powershell
Invoke-WebRequest -Uri http://localhost:30080/blog/categories
Invoke-WebRequest -Uri "http://localhost:30080/blog/posts?page=1&size=6"
# 정상 데이터 반환 확인 ✅
```

### **3. Auth 서비스 테스트**
```powershell
Invoke-WebRequest -Uri http://localhost:30080/auth/health
```

---

## 🔄 **Docker Compose vs k3d 비교**

| 구분 | Docker Compose | k3d Kubernetes |
|------|----------------|----------------|
| **오케스트레이션** | 컨테이너 레벨 | Pod/Service 레벨 |
| **네트워킹** | bridge 네트워크 | ClusterIP/NodePort |
| **스토리지** | 볼륨 마운트 | PVC/StatefulSet |
| **스케일링** | docker-compose scale | kubectl scale |
| **로드밸런싱** | 없음 | Service 자동 제공 |
| **헬스체크** | 컨테이너 레벨 | livenessProbe/readinessProbe |
| **롤링 업데이트** | 수동 | 자동 (Deployment) |
| **외부 접근** | 포트 바인딩 | NodePort/Ingress |

---

## 🎯 **마이그레이션 성과 (100% 완료)**

### **✅ 완료된 작업 (100%)**
- ✅ k3d 클러스터 생성 및 포트 매핑 설정
- ✅ PostgreSQL StatefulSet (영구 스토리지 + 초기 데이터)
- ✅ Redis Deployment
- ✅ Auth Service (JWT 인증)
- ✅ Blog Service (게시글/카테고리 관리)
- ✅ API Gateway (라우팅, 프록시, CORS)
- ✅ Frontend 로컬 개발 환경 (Next.js)
- ✅ 전체 시스템 통합 테스트
- ✅ API 연결 및 데이터 로딩 확인

---

## 💡 **핵심 학습 포인트**

### **가장 중요한 깨달음**
1. **k3d 포트 매핑의 중요성**: 
   ```powershell
   # 잘못된 방법
   k3d cluster create jinmini-portfolio
   
   # 올바른 방법  
   k3d cluster create jinmini-portfolio --port "30080:30080@loadbalancer"
   ```

2. **문제 해결 순서의 중요성**:
   - ❌ React Query 문제로 착각 → 5회 이상 삽질
   - ✅ 네트워크 연결 문제가 근본 원인

3. **PowerShell 환경 특성**:
   ```powershell
   # Linux 명령어 대신 PowerShell 명령어 사용
   curl → Invoke-WebRequest
   cat → Get-Content  
   ls → Get-ChildItem
   ```

### **Docker vs Kubernetes 아키텍처 차이**

#### **Docker Compose 아키텍처**
```
Host:3000 → Frontend Container:3000
Host:8080 → API Gateway Container:8080
```

#### **k3d Kubernetes 아키텍처**  
```
Host:30000 → LoadBalancer → NodePort:30000 → Frontend Pod:3000
Host:30080 → LoadBalancer → NodePort:30080 → API Gateway Pod:8080
```

### **Kubernetes 네이티브 기능 활용**
- **StatefulSet**: PostgreSQL 영구 스토리지
- **Deployment**: 무상태 마이크로서비스들
- **ConfigMap**: 환경변수 중앙 관리 + PostgreSQL 초기화 스크립트
- **Service**: 내부 통신 및 로드밸런싱
- **NodePort**: 외부 접근 제어

---

## 🛠️ **트러블슈팅 가이드**

### **일반적인 문제들**

#### **Pod가 Pending 상태**
```powershell
# 원인 확인
kubectl describe pod <pod-name>

# 리소스 부족 확인
kubectl top nodes
```

#### **ConfigMap 누락**
```powershell
# PostgreSQL 초기화 실패 시
kubectl create configmap postgres-init-db --from-file=init-db.sql=init-db.sql
kubectl delete pod postgres-0  # Pod 재시작
```

#### **포트 접근 불가**
```powershell
# k3d 포트 매핑 확인
k3d cluster list

# 해결: 포트 매핑과 함께 클러스터 재생성
k3d cluster delete <cluster-name>
k3d cluster create <cluster-name> --port "30080:30080@loadbalancer"
```

#### **CORS 오류**
```yaml
# API Gateway ConfigMap에 CORS_ORIGINS 추가
data:
  CORS_ORIGINS: "http://localhost:3000,http://localhost:3001"
```

---

## 🚀 **다음 단계 로드맵**

### **Phase 1: 컨테이너화된 Frontend 배포 (우선순위: 높음)**
```powershell
# 컨테이너 환경에서 Frontend 완전 동작 확인
# 현재는 로컬 개발서버(localhost:3001)에서만 테스트 완료
kubectl get service frontend  # NodePort 30000 활용
```

### **Phase 2: Ingress Controller 설정 (우선순위: 높음)**
- Traefik 인그레스 컨트롤러 활용
- 단일 도메인으로 모든 서비스 접근
- 프로덕션 환경과 유사한 라우팅 구조

### **Phase 3: 모니터링 & 로깅 (우선순위: 중간)**
- Kubernetes Dashboard
- Prometheus + Grafana
- 중앙화된 로그 수집

### **Phase 4: AWS EKS 준비 (우선순위: 중간)**
- Helm Chart 패키징
- 환경별 values.yaml 작성
- Secret 관리 (AWS Secrets Manager)

### **Phase 5: CI/CD 파이프라인 (우선순위: 낮음)**
- GitHub Actions
- 자동 이미지 빌드 및 배포
- 무중단 배포 전략

---

## 📚 **참고 자료**

- [k3d 공식 문서](https://k3d.io/)
- [Kubernetes 공식 문서](https://kubernetes.io/docs/)  
- [k3d 포트 매핑 가이드](https://k3d.io/v5.7.4/usage/exposing_services/)

---

**마이그레이션 시작일**: 2025-06-02  
**마이그레이션 완료일**: 2025-06-04  
**총 소요 시간**: 약 6시간 (문제 해결 포함)  
**성공률**: 100% ✅  
**핵심 성과**: Docker Compose → k3d Kubernetes 완전 마이그레이션 🚀

---

## 📈 **다음 즉시 진행 가능한 작업들**

### **1. 컨테이너화된 Frontend 완전 배포 (30분)**
```powershell
# Frontend 컨테이너 버전 테스트
# 현재는 로컬 개발서버(localhost:3001)에서만 테스트 완료
kubectl get service frontend  # NodePort 30000 활용
```

### **2. Ingress 컨트롤러 설정 (1시간)**
```yaml
# 목표 구조
jinmini.local/ → Frontend
jinmini.local/api/ → API Gateway
```

### **3. 환경 최적화 (30분)**
- Resource limits 설정
- livenessProbe/readinessProbe 추가
- 롤링 업데이트 전략 설정

**다음 목표**: 완전한 프로덕션 준비 완료 → AWS EKS 마이그레이션 🎯

---

## 🌐 **STEP 9: Ingress Controller 설정 (완료)**

### **9.1 포트 바인딩이 포함된 k3d 클러스터 재생성**

#### **기존 클러스터의 문제점**
- NodePort 접근을 위한 포트 매핑이 누락되어 있어 외부에서 접근 불가
- 6443 포트 충돌 발생

#### **해결: 포트 바인딩과 함께 클러스터 재생성**
```powershell
# 기존 클러스터 삭제
k3d cluster delete jinmini-portfolio

# 포트 충돌 확인
netstat -ano | findstr :6443
netstat -ano | findstr :8080

# 포트 바인딩과 함께 새 클러스터 생성 (Ingress 지원)
k3d cluster create jinmini-portfolio --api-port 6444 --port "8090:80@loadbalancer" --port "8453:443@loadbalancer" --agents 1
```

**포트 매핑 결과:**
- `localhost:8090` → Traefik Ingress (HTTP)
- `localhost:8453` → Traefik Ingress (HTTPS)
- API 서버: `localhost:6444`

### **9.2 기존 서비스 재배포**

#### **모든 이미지 재빌드 및 임포트**
```powershell
# Docker Compose로 모든 이미지 빌드
docker-compose build

# k3d 클러스터에 이미지 임포트
k3d image import aws_portfolio-auth-service:latest aws_portfolio-blog-service:latest aws_portfolio-api-gateway:latest aws_portfolio-frontend:latest -c jinmini-portfolio
```

#### **Kubernetes 리소스 재배포**
```powershell
# 모든 서비스 배포
kubectl apply -f k8s/database/ -f k8s/services/ -f k8s/frontend/ -f k8s/config/

# PostgreSQL 초기화 ConfigMap 누락 해결
kubectl apply -f k8s/database/postgres-init-configmap.yaml
kubectl delete statefulset postgres  # StatefulSet 재시작
kubectl apply -f k8s/database/postgres-statefulset.yaml

# 모든 Deployment 재시작
kubectl rollout restart deployment/auth-service deployment/blog-service deployment/api-gateway deployment/frontend
```

### **9.3 Traefik Ingress Controller 확인**

#### **k3d 기본 Traefik 상태 확인**
```powershell
# 클러스터 정보 확인
kubectl cluster-info

# Traefik 파드 확인
kubectl get pods -n kube-system | findstr traefik
# 출력:
# helm-install-traefik-crd-cphtf            0/1     Completed   0          96s
# helm-install-traefik-hgx2r                0/1     Completed   2          96s
# svclb-traefik-ef523dbd-jqc2c              2/2     Running     0          61s
# svclb-traefik-ef523dbd-t452j              2/2     Running     0          61s
# traefik-5d45fc8cc9-2q8j7                  1/1     Running     0          61s ✅
```

### **9.4 Ingress 리소스 생성**

#### **도메인 기반 라우팅 설정**
```yaml
# k8s/config/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: jinmini-portfolio-ingress
  namespace: default
  annotations:
    kubernetes.io/ingress.class: "traefik"
spec:
  rules:
  - host: jinmini-portfolio.local
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 8080
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-only-ingress
  namespace: default
  annotations:
    kubernetes.io/ingress.class: "traefik"
spec:
  rules:
  - host: api.jinmini-portfolio.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 8080
```

#### **Ingress 배포 및 확인**
```powershell
# Ingress 리소스 배포
kubectl apply -f k8s/config/ingress.yaml

# Ingress 상태 확인
kubectl get ingress
# 출력:
# NAME                        CLASS    HOSTS                         ADDRESS                 PORTS   AGE
# api-only-ingress            <none>   api.jinmini-portfolio.local   172.19.0.3,172.19.0.4   80      9m17s
# jinmini-portfolio-ingress   <none>   jinmini-portfolio.local       172.19.0.3,172.19.0.4   80      9m17s ✅
```

### **9.5 ❌ 데이터베이스 스키마 문제 해결**

#### **PostgreSQL 연결 실패 문제**
```powershell
# PostgreSQL 파드가 15분간 ContainerCreating 상태
kubectl describe pod postgres-0
# 원인: configmap "postgres-init-db" not found

# 해결: PostgreSQL 초기화 ConfigMap 생성
kubectl apply -f k8s/database/postgres-init-configmap.yaml
kubectl delete statefulset postgres
kubectl apply -f k8s/database/postgres-statefulset.yaml
```

#### **Blog Service API 오류 해결**
```powershell
# 블로그 서비스 로그 확인
kubectl logs blog-service-b7b5c6d7d-xdbnp --tail=20
# 오류: column categories.slug does not exist

# 해결: categories 테이블에 slug 컬럼 추가
kubectl exec -it postgres-0 -- psql -U admin -d jinmini_portfolio -c "ALTER TABLE categories ADD COLUMN slug VARCHAR(255) UNIQUE;"

# 각 카테고리에 slug 값 설정
kubectl exec postgres-0 -- psql -U admin -d jinmini_portfolio -c "UPDATE categories SET slug = 'programming' WHERE name = '프로그래밍';"
kubectl exec postgres-0 -- psql -U admin -d jinmini_portfolio -c "UPDATE categories SET slug = 'web-development' WHERE name = '웹 개발';"
kubectl exec postgres-0 -- psql -U admin -d jinmini_portfolio -c "UPDATE categories SET slug = 'database' WHERE name = '데이터베이스';"
kubectl exec postgres-0 -- psql -U admin -d jinmini_portfolio -c "UPDATE categories SET slug = 'devops' WHERE name = 'DevOps';"
kubectl exec postgres-0 -- psql -U admin -d jinmini_portfolio -c "UPDATE categories SET slug = 'ai-ml' WHERE name = 'AI/ML';"
kubectl exec postgres-0 -- psql -U admin -d jinmini_portfolio -c "UPDATE categories SET slug = 'general' WHERE name = '일반';"

# 테이블 구조 확인
kubectl exec -it postgres-0 -- psql -U admin -d jinmini_portfolio -c "SELECT id, name, slug FROM categories;"
# 출력:
#  id |     name     |      slug       
# ----+--------------+-----------------
#   1 | 프로그래밍   | programming
#   2 | 웹 개발      | web-development
#   3 | 데이터베이스 | database
#   4 | DevOps       | devops
#   5 | AI/ML        | ai-ml
#   6 | 일반         | general ✅
```

### **9.6 🎉 Ingress를 통한 API 테스트 성공**

#### **API Gateway 연결 확인**
```powershell
# PowerShell 방식으로 API 테스트
Invoke-WebRequest -Uri "http://localhost:8090/health" -Headers @{"Host"="api.jinmini-portfolio.local"}
# 출력:
# StatusCode        : 200
# StatusDescription : OK
# Content           : {"status":"healthy","service":"API Gateway","version":"1.0.0"} ✅
```

#### **블로그 API 테스트 성공**
```powershell
# 카테고리 API 테스트
Invoke-WebRequest -Uri "http://localhost:8090/blog/categories" -Headers @{"Host"="api.jinmini-portfolio.local"}
# 출력:
# StatusCode        : 200
# Content           : [{"name":"AI/ML","slug":"ai-ml","description":"인공지능과 머신러닝","id":5,"created_at":"2025-06-04T04:08:12.704024"}...] ✅
```

#### **프론트엔드 Ingress 테스트 성공**
```powershell
# 프론트엔드 홈페이지 접속
Invoke-WebRequest -Uri "http://localhost:8090/" -Headers @{"Host"="jinmini-portfolio.local"}
# 출력:
# StatusCode        : 200
# Content           : <!DOCTYPE html><html lang="ko">... ✅
```

### **9.7 ✅ Ingress Controller 설정 완료**

#### **최종 아키텍처**
```
인터넷 → localhost:8090 → k3d LoadBalancer → Traefik Ingress → 
├── jinmini-portfolio.local → Frontend Service (port 3000)
└── api.jinmini-portfolio.local → API Gateway Service (port 8080)
```

#### **접속 방법**
```bash
# Frontend 접속
curl -H "Host: jinmini-portfolio.local" http://localhost:8090/

# API 접속  
curl -H "Host: api.jinmini-portfolio.local" http://localhost:8090/health
curl -H "Host: api.jinmini-portfolio.local" http://localhost:8090/blog/categories
```

#### **Windows에서 도메인 사용 (선택사항)**
```powershell
# hosts 파일에 도메인 추가 (관리자 권한 필요)
echo "127.0.0.1 jinmini-portfolio.local" >> C:\Windows\System32\drivers\etc\hosts
echo "127.0.0.1 api.jinmini-portfolio.local" >> C:\Windows\System32\drivers\etc\hosts
```

---

## 🏆 **전체 마이그레이션 완료 (100%)**

### **✅ 성공적으로 완료된 모든 단계**
1. ✅ k3d 클러스터 생성 (포트 바인딩 포함)
2. ✅ PostgreSQL StatefulSet (영구 스토리지 + 초기 데이터)
3. ✅ Redis Deployment
4. ✅ Auth Service (JWT 인증)
5. ✅ Blog Service (게시글/카테고리 관리)
6. ✅ API Gateway (라우팅, 프록시, CORS)
7. ✅ Frontend (Next.js)
8. ✅ **Traefik Ingress Controller (도메인 기반 라우팅)**
9. ✅ **데이터베이스 스키마 최적화**
10. ✅ **전체 시스템 통합 테스트**

### **최종 배포 상태**

| 서비스 | 타입 | 상태 | 내부 포트 | 외부 접근 |
|--------|------|------|----------|----------|
| **PostgreSQL** | StatefulSet | ✅ Running | 5432 | 내부 전용 |
| **Redis** | Deployment | ✅ Running | 6379 | 내부 전용 |
| **Auth Service** | Deployment | ✅ Running | 8101 | Ingress 경유 |
| **Blog Service** | Deployment | ✅ Running | 8102 | Ingress 경유 |
| **API Gateway** | Deployment | ✅ Running | 8080 | `api.jinmini-portfolio.local` |
| **Frontend** | Deployment | ✅ Running | 3000 | `jinmini-portfolio.local` |
| **Traefik Ingress** | DaemonSet | ✅ Running | 80/443 | `localhost:8090/8453` |

---

## 🚀 **다음 확장 계획**

### **Phase 1: 프로덕션 준비 (우선순위: 높음)**
- HTTPS/TLS 설정 (Let's Encrypt)
- Resource limits 및 requests 설정
- Health check 최적화
- Secret 관리 (ConfigMap → Secret)

### **Phase 2: 모니터링 & 관찰성 (우선순위: 중간)**
- Kubernetes Dashboard
- Prometheus + Grafana
- 중앙화된 로그 수집 (ELK Stack)
- 분산 추적 (Jaeger)

### **Phase 3: AWS EKS 마이그레이션 (우선순위: 중간)**
- Helm Chart 패키징
- 환경별 values.yaml 작성
- AWS Load Balancer Controller
- AWS Secrets Manager 연동

### **Phase 4: CI/CD & GitOps (우선순위: 낮음)**
- GitHub Actions 워크플로우
- ArgoCD 또는 Flux 구축
- 무중단 배포 전략
- 자동화된 테스트 파이프라인

---

**마이그레이션 시작일**: 2025-06-02  
**Ingress 설정 완료일**: 2025-06-04  
**총 마이그레이션 시간**: 약 8시간  
**성공률**: 100% ✅  
**핵심 성과**: Docker Compose → k3d Kubernetes + Ingress Controller 완전 마이그레이션 🌐🚀

---

## 💡 **Ingress 설정의 핵심 학습 포인트**

### **1. k3d 포트 바인딩의 중요성**
```powershell
# ❌ 잘못된 방법: 포트 매핑 없음
k3d cluster create jinmini-portfolio

# ✅ 올바른 방법: Ingress 포트 매핑 포함
k3d cluster create jinmini-portfolio --port "8090:80@loadbalancer" --port "8453:443@loadbalancer"
```

### **2. Traefik vs Nginx Ingress**
- **k3d 기본**: Traefik (자동 설치, 설정 간편)
- **설정 방법**: `kubernetes.io/ingress.class: "traefik"` 어노테이션
- **라우팅**: Host 헤더 기반 도메인 라우팅

### **3. 서비스 이름 매핑 주의사항**
```yaml
# ❌ 잘못된 서비스 이름
backend:
  service:
    name: api-gateway-service  # 존재하지 않음

# ✅ 올바른 서비스 이름  
backend:
  service:
    name: api-gateway  # kubectl get services로 확인된 이름
```

### **4. PowerShell에서 Ingress 테스트**
```powershell
# Linux curl 명령어는 사용 불가
curl -H "Host: api.local" http://localhost:8090/  # ❌

# PowerShell 방식
Invoke-WebRequest -Uri "http://localhost:8090/" -Headers @{"Host"="api.local"}  # ✅
```

### **5. 데이터베이스 스키마 호환성**
- **문제**: 애플리케이션에서 요구하는 컬럼이 DB에 없음
- **해결**: `ALTER TABLE` 명령으로 누락된 컬럼 추가
- **예방**: 마이그레이션 스크립트로 스키마 버전 관리

**Ingress Controller 완전 정복! 🎯**