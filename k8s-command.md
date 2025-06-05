# k3d & Kubernetes 상황별 명령어 가이드

**작성일**: 2025-06-04  
**대상**: k3d + Kubernetes 환경 (Windows PowerShell)  
**참고**: PowerShell 환경에서는 `curl` 대신 `Invoke-WebRequest` 사용

---

## 🚀 **클러스터 관리**

### **클러스터 생성/삭제**
```powershell
# k3d 클러스터 생성 (기본)
k3d cluster create jinmini-portfolio

# Ingress 포트 바인딩과 함께 클러스터 생성
k3d cluster create jinmini-portfolio --api-port 6444 --port "8090:80@loadbalancer" --port "8453:443@loadbalancer" --agents 1

# 클러스터 목록 확인
k3d cluster list

# 클러스터 삭제
k3d cluster delete jinmini-portfolio
```

### **클러스터 상태 확인**
```powershell
# 클러스터 정보 확인
kubectl cluster-info

# 노드 상태 확인
kubectl get nodes -o wide

# 클러스터 전체 리소스 확인
kubectl get all --all-namespaces
```

---

## 📦 **이미지 관리**

### **Docker 이미지 빌드 및 k3d 임포트**
```powershell
# Docker Compose로 모든 이미지 빌드
docker-compose build

# 특정 서비스만 빌드
docker-compose build auth-service
docker-compose build blog-service
docker-compose build api-gateway
docker-compose build frontend

# k3d 클러스터에 이미지 임포트 (단일)
k3d image import aws_portfolio-auth-service:latest -c jinmini-portfolio

# k3d 클러스터에 이미지 임포트 (다중)
k3d image import aws_portfolio-auth-service:latest aws_portfolio-blog-service:latest aws_portfolio-api-gateway:latest aws_portfolio-frontend:latest -c jinmini-portfolio
```

---

## 🏗️ **리소스 배포 및 관리**

### **ConfigMap & Secret**
```powershell
# ConfigMap 생성 (파일에서)
kubectl create configmap postgres-init-db --from-file=init-db.sql=init-db.sql

# ConfigMap 조회
kubectl get configmap
kubectl get configmap postgres-init-db -o yaml

# ConfigMap 삭제
kubectl delete configmap postgres-init-db
```

### **배포 명령어**
```powershell
# 단일 파일 배포
kubectl apply -f k8s/database/postgres-statefulset.yaml

# 디렉토리 단위 배포
kubectl apply -f k8s/database/
kubectl apply -f k8s/services/
kubectl apply -f k8s/frontend/
kubectl apply -f k8s/config/

# 재귀적 배포 (모든 하위 디렉토리)
kubectl apply -f k8s/ -R

# 리소스 삭제
kubectl delete -f k8s/database/postgres-statefulset.yaml
```

---

## 🔍 **상태 확인 및 디버깅**

### **파드 상태 확인**
```powershell
# 모든 파드 상태 확인
kubectl get pods

# 파드 상태 자세히 확인 (IP, 노드 정보 포함)
kubectl get pods -o wide

# 특정 라벨의 파드만 확인
kubectl get pods -l app=postgres
kubectl get pods -l app=auth-service

# 실시간 파드 상태 모니터링
kubectl get pods -w

# 파드 상태 필터링
kubectl get pods | findstr postgres
kubectl get pods | findstr Running
kubectl get pods | findstr Error
```

### **상세 정보 및 로그**
```powershell
# 파드 상세 정보 확인
kubectl describe pod postgres-0
kubectl describe pod auth-service-596c778879-nt8th

# 서비스 상세 정보 확인
kubectl describe service postgres
kubectl describe deployment auth-service

# 파드 로그 확인
kubectl logs postgres-0
kubectl logs auth-service-596c778879-nt8th

# 로그 실시간 스트리밍
kubectl logs -f auth-service-596c778879-nt8th

# 로그 마지막 N줄만 확인
kubectl logs auth-service-596c778879-nt8th --tail=20

# 특정 시간 이후 로그
kubectl logs auth-service-596c778879-nt8th --since=10m
```

---

## 🌐 **서비스 및 네트워킹**

### **서비스 확인**
```powershell
# 모든 서비스 확인
kubectl get services
kubectl get svc

# 서비스 상세 정보
kubectl describe service api-gateway
kubectl describe service postgres

# 엔드포인트 확인
kubectl get endpoints
```

### **Ingress 관리**
```powershell
# Ingress 리소스 확인
kubectl get ingress

# Ingress 상세 정보
kubectl describe ingress api-only-ingress
kubectl describe ingress jinmini-portfolio-ingress

# Traefik Ingress Controller 확인
kubectl get pods -n kube-system | findstr traefik
```

---

## 🔄 **배포 관리**

### **Deployment 관리**
```powershell
# Deployment 상태 확인
kubectl get deployments
kubectl get deploy

# Deployment 재시작
kubectl rollout restart deployment/auth-service
kubectl rollout restart deployment/blog-service
kubectl rollout restart deployment/api-gateway
kubectl rollout restart deployment/frontend

# 모든 Deployment 재시작
kubectl rollout restart deployment/auth-service deployment/blog-service deployment/api-gateway deployment/frontend

# 롤아웃 상태 확인
kubectl rollout status deployment/auth-service

# 롤아웃 히스토리
kubectl rollout history deployment/auth-service

# 이전 버전으로 롤백
kubectl rollout undo deployment/auth-service
```

### **StatefulSet 관리**
```powershell
# StatefulSet 확인
kubectl get statefulsets
kubectl get sts

# StatefulSet 삭제 및 재생성
kubectl delete statefulset postgres
kubectl apply -f k8s/database/postgres-statefulset.yaml

# PVC 확인 (StatefulSet의 영구 볼륨)
kubectl get pvc
```

---

## 💾 **데이터베이스 관리**

### **PostgreSQL 접근**
```powershell
# PostgreSQL 컨테이너 접속
kubectl exec -it postgres-0 -- bash

# PostgreSQL 직접 쿼리 실행
kubectl exec -it postgres-0 -- psql -U admin -d jinmini_portfolio -c "SELECT * FROM users;"
kubectl exec -it postgres-0 -- psql -U admin -d jinmini_portfolio -c "SELECT * FROM categories;"
kubectl exec -it postgres-0 -- psql -U admin -d jinmini_portfolio -c "SELECT * FROM posts;"

# 테이블 구조 확인
kubectl exec -it postgres-0 -- psql -U admin -d jinmini_portfolio -c "\d users"
kubectl exec -it postgres-0 -- psql -U admin -d jinmini_portfolio -c "\d categories"
kubectl exec -it postgres-0 -- psql -U admin -d jinmini_portfolio -c "\d posts"

# 스키마 수정 (컬럼 추가)
kubectl exec -it postgres-0 -- psql -U admin -d jinmini_portfolio -c "ALTER TABLE categories ADD COLUMN slug VARCHAR(255) UNIQUE;"

# 데이터 업데이트
kubectl exec postgres-0 -- psql -U admin -d jinmini_portfolio -c "UPDATE categories SET slug = 'programming' WHERE name = '프로그래밍';"
```

---

## 🧪 **API 테스트 (PowerShell)**

### **NodePort를 통한 직접 접근**
```powershell
# API Gateway 헬스체크
Invoke-WebRequest -Uri http://localhost:30080/health

# 블로그 카테고리 API
Invoke-WebRequest -Uri http://localhost:30080/blog/categories

# 블로그 포스트 API (페이지네이션)
Invoke-WebRequest -Uri "http://localhost:30080/blog/posts?page=1&size=6"

# Auth 서비스 헬스체크
Invoke-WebRequest -Uri http://localhost:30080/auth/health
```

### **Ingress를 통한 도메인 접근**
```powershell
# API Gateway (Host 헤더 사용)
Invoke-WebRequest -Uri "http://localhost:8090/health" -Headers @{"Host"="api.jinmini-portfolio.local"}
Invoke-WebRequest -Uri "http://localhost:8090/blog/categories" -Headers @{"Host"="api.jinmini-portfolio.local"}

# Frontend (Host 헤더 사용)
Invoke-WebRequest -Uri "http://localhost:8090/" -Headers @{"Host"="jinmini-portfolio.local"}
```

---

## 🛠️ **트러블슈팅**

### **일반적인 문제 해결**
```powershell
# Pod가 Pending 상태일 때
kubectl describe pod <pod-name>
kubectl get events --sort-by=.metadata.creationTimestamp

# ConfigMap 누락 문제
kubectl get configmap
kubectl create configmap postgres-init-db --from-file=init-db.sql=init-db.sql

# 이미지 pull 실패
k3d image import <image-name>:latest -c jinmini-portfolio

# 서비스 연결 문제
kubectl get endpoints
kubectl describe service <service-name>

# 포트 접근 불가
kubectl get services
kubectl port-forward <pod-name> <local-port>:<pod-port>

# 리소스 정리
kubectl delete pods --all
kubectl delete deployments --all
kubectl delete services --all --ignore-not-found=true
```

### **로그 및 디버깅**
```powershell
# 특정 서비스의 모든 파드 로그
kubectl logs -l app=auth-service --all-containers=true

# 이전 실행된 컨테이너 로그
kubectl logs <pod-name> --previous

# 다중 컨테이너 파드에서 특정 컨테이너 로그
kubectl logs <pod-name> -c <container-name>

# 클러스터 전체 이벤트 확인
kubectl get events --all-namespaces --sort-by=.metadata.creationTimestamp
```

---

## 🎯 **자주 사용하는 조합 명령어**

### **전체 재배포 워크플로우**
```powershell
# 1. 이미지 재빌드
docker-compose build

# 2. k3d에 이미지 임포트
k3d image import aws_portfolio-auth-service:latest aws_portfolio-blog-service:latest aws_portfolio-api-gateway:latest aws_portfolio-frontend:latest -c jinmini-portfolio

# 3. 모든 리소스 재배포
kubectl apply -f k8s/ -R

# 4. Deployment 재시작
kubectl rollout restart deployment/auth-service deployment/blog-service deployment/api-gateway deployment/frontend

# 5. 상태 확인
kubectl get pods
kubectl get services
kubectl get ingress
```

### **빠른 상태 점검**
```powershell
# 한 번에 모든 상태 확인
kubectl get all
kubectl get pods,svc,ingress
kubectl get pods | findstr -v Running  # 문제 있는 파드 찾기
```

### **완전 정리 및 재시작**
```powershell
# 클러스터 완전 재생성
k3d cluster delete jinmini-portfolio
k3d cluster create jinmini-portfolio --api-port 6444 --port "8090:80@loadbalancer" --port "8453:443@loadbalancer" --agents 1

# 이미지 재임포트 및 전체 배포
k3d image import aws_portfolio-auth-service:latest aws_portfolio-blog-service:latest aws_portfolio-api-gateway:latest aws_portfolio-frontend:latest -c jinmini-portfolio
kubectl apply -f k8s/ -R
```

---

## 📚 **유용한 별칭 (PowerShell Profile)**

```powershell
# PowerShell Profile에 추가할 별칭들
Set-Alias k kubectl
function kgp { kubectl get pods }
function kgs { kubectl get services }
function kgi { kubectl get ingress }
function kaf { kubectl apply -f $args }
function kdel { kubectl delete -f $args }
function klogs { kubectl logs $args }
function kdesc { kubectl describe $args }

# 사용 예시
k get pods        # kubectl get pods
kgp              # kubectl get pods  
kaf k8s/database/ # kubectl apply -f k8s/database/
```

---

**마지막 업데이트**: 2025-06-04  
**환경**: Windows PowerShell + k3d + Kubernetes  
**테스트 완료**: ✅ 모든 명령어 실전 검증됨
