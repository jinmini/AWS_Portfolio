## 제품 요구사항 정의서 (Product Requirements Document - PRD)

**문서명:** AWS 클라우드 환경 Kubernetes (K3s) 기반 애플리케이션 자동 배포 시스템 구축

**버전:** 1.0
**작성일:** 2025년 06월 04일

---

### 1. 도입 (Introduction)

#### 1.1. 문서 목적
본 문서는 기존 Docker 기반으로 운영되던 AWS Portfolio 애플리케이션의 배포 환경을 Kubernetes (K3s) 기반으로 전환하고, 이를 AWS 클라우드 환경에서 효율적이고 안정적으로 자동화하기 위한 요구사항을 정의합니다. 이는 개발-배포 주기를 단축하고, 시스템의 확장성 및 가용성을 향상시키는 것을 목표로 합니다.

#### 1.2. 배경
현재 AWS Portfolio 애플리케이션은 Docker 또는 Docker Compose 기반으로 단일 호스트에서 컨테이너화되어 운영되고 있습니다. 
이 방식은 초기 개발 및 테스트에는 적합하지만, 서비스의 확장, 안정성, 로드 밸런싱, 자동 복구 등의 측면에서 한계가 있습니다. Kubernetes(K3s)로의 전환은 이러한 문제들을 해결하고, AWS 클라우드의 장점을 최대한 활용하여 더욱 견고한 운영 환경을 구축하기 위함입니다.

#### 1.3. 목표
*   AWS 클라우드 환경에 K3s 클러스터를 성공적으로 구축하고 애플리케이션 배포
*   Frontend, Backend(API Gateway) 애플리케이션의 안정적인 컨테이너화 및 Kubernetes 배포
*   외부 사용자의 애플리케이션 접근을 위한 Ingress 기반 라우팅 자동화
*   클러스터 내부 서비스 간의 효율적인 통신 구조 확립
*   애플리케이션 환경 설정 및 비밀 데이터의 안전한 관리
*   애플리케이션 데이터의 영구적 저장 및 관리
*   코드 변경부터 배포까지의 CI/CD (지속적 통합/배포) 파이프라인 자동화
*   시스템 운영의 가시성 확보 (로깅 및 모니터링 기반 마련)

---

### 2. 배포 아키텍처 및 구성 (Deployment Architecture & Components)

#### 2.1. 고수준 아키텍처
```
+------------------+     +-------------------------------------+
| 사용자 브라우저  | <-> |  AWS Load Balancer / DNS (Public IP)|
+------------------+     +-------------------------------------+
                                     |
                                     v
+-----------------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                          K3s (Kubernetes) Cluster on AWS EC2                                                              |
| +-----------------+    +-----------------+    +-----------------+     +-----------------+    +-----------------+    +-----------------+                  |
| |  K3s Node 1     |    |  K3s Node 2     |    |  K3s Node N     |     |  K3s Node 1     |    |  K3s Node 2     |    |  K3s Node N     |                  |
| |  (Master/Agent) |    |  (Agent)        |    |  (Agent)        | ... |  (Master/Agent) |    |  (Agent)        |    |  (Agent)        |                  |
| |                 |    |                 |    |                 |     |                 |    |                 |    |                 |                  |
| | +-------------+ |    | +-------------+ |    | +-------------+ |     | +-------------+ |    | +-------------+ |    | +-------------+ |                  |
| | | Ingress     | |    | | Frontend    | |    | | Backend     | |     | | Frontend    | |    | | Backend     | |    | | Database    | |                  |
| | | Controller  | |    | | Pod (N)     | |    | | Pod (M)     | |     | | Pod (N+1)   | |    | | Pod (M+1)   | |    | | Pod (DB)    | |                  |
| | | (Traefik)   | |    | | (Container) | |    | | (Container) | |     | | (Container) | |    | | (Container) | |    | | (Container) | |                  |
| | +------+------+ |    | +------+------+ |    | +------+------+ |     | +------+------+ |    | +------+------+ |    | +------+------+ |                  |
| |        ^        |    |        ^        |    |        ^        |     |        ^        |    |        ^        |    |        ^        |                  |
| +--------|--------+    +--------|--------+    +--------|--------+     +--------|--------+    +--------|--------+    +--------|--------+                  |
|          |                 |                  |                   |                |                  |                  |                                   |
|          |                 |                  |                   |                |                  |                  |                                   |
|          |                 +------------------+-------------------+                +------------------+-------------------+                                   |
|          |                                   Service (ClusterIP)                                       Service (ClusterIP)                                    |
|          |               (frontend-service:3000)                                                     (api-gateway-service:8080)                               |
|          |                                                                                                                                                    |
|          +----------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                                    K3s Internal Network                                                                      |
|                                                                                                                                                                |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------+
```
*(참고: 위 아키텍처는 텍스트 기반으로 간략화되었으며, 실제 배포는 더 복잡한 네트워크 구성과 보안 그룹을 포함합니다.)*

#### 2.2. 핵심 구성 요소
*   **K3s Cluster:** AWS EC2 인스턴스에 배포되는 경량 Kubernetes 클러스터.
*   **Frontend 애플리케이션:** Next.js 
*   **Backend 애플리케이션:** API Gateway (FastAPI)
*   **Database:** PostgreSQL 

#### 2.3. Kubernetes Object (YAML) 및 역할
*   **`Deployment`:** 애플리케이션 Pod(컨테이너)의 배포, 스케일링, 업데이트를 관리합니다. (Frontend, Backend, Database 각각)
*   **`Service`:** 클러스터 내부에서 Pod 그룹에 대한 안정적인 네트워크 접근(ClusterIP, DNS)을 제공하고 로드 밸런싱을 수행합니다.
    *   `frontend-service` (port: 3000, targetPort: 3000)
    *   `api-gateway-service` (port: 8080, targetPort: 8080)
    *   `postgresql-service` (port: 5432, targetPort: 5432)
*   **`Ingress`:** 외부 HTTP/HTTPS 트래픽을 클러스터 내부의 `Service`로 라우팅하는 규칙을 정의합니다. K3s 내장 Traefik Ingress Controller가 사용됩니다.
    *   예: `my-app.example.com/` -> `frontend-service`
    *   예: `my-app.example.com/api` -> `api-gateway-service`
*   **`ConfigMap`:** 애플리케이션의 일반적인 환경 설정 데이터를 저장합니다. `NEXT_PUBLIC_API_URL`과 같은 브라우저 기반 Frontend 애플리케이션이 접근할 외부 API URL을 관리합니다.
*   **`Secret`:** 민감한 정보(예: 데이터베이스 비밀번호, API 키)를 안전하게 저장합니다.
*   **`PersistentVolumeClaim` (PVC):** 데이터베이스와 같이 영구적인 데이터 저장이 필요한 Pod를 위해 스토리지 요청을 정의합니다.
*   **`PersistentVolume` (PV):** 실제 물리적 또는 클라우드 스토리지 자원을 나타내며, `StorageClass`에 의해 동적으로 프로비저닝됩니다.
*   **`StorageClass`:** K3s의 `local-path` 또는 AWS EBS/EFS와 같은 특정 스토리지 프로비저너를 정의합니다.

#### 2.4. 데이터 통신 Flow
1.  **사용자 (브라우저) -> Frontend:**
    *   사용자는 브라우저를 통해 외부 도메인(`my-app.example.com`) 또는 노드 IP+NodePort(`http://<Node_IP>:30080`)로 Frontend에 접속합니다.
    *   DNS는 K3s 노드의 Public IP (또는 앞단의 AWS Load Balancer IP)를 가리킵니다.
    *   K3s 노드의 Traefik Ingress Controller가 요청을 받아 `Ingress` 규칙에 따라 `frontend-service`로 라우팅합니다.
    *   `frontend-service`는 트래픽을 `frontend` Pod로 전달합니다.

2.  **Frontend (브라우저) -> Backend (API Gateway):**
    *   브라우저에 로드된 `frontend` 애플리케이션의 JavaScript 코드는 `ConfigMap`에 정의된 `NEXT_PUBLIC_API_URL` 값(`http://my-app.example.com/api` 또는 `http://<Node_IP>:30080/api`)을 사용하여 Backend API에 요청을 보냅니다.
    *   이 요청은 다시 Ingress Controller를 통해 `api-gateway-service`로 라우팅되고, 최종적으로 `api-gateway` Pod로 전달됩니다.

3.  **Backend (API Gateway) -> Database:**
    *   `api-gateway` Pod는 클러스터 내부 DNS 이름(`postgresql-service:5432`)을 사용하여 Database Pod로 요청을 보냅니다.
    *   `postgresql-service`는 `postgresql` Pod로 트래픽을 전달합니다.

---

### 3. 주요 기능 요구사항 (Key Feature Requirements)

#### 3.1. 애플리케이션 컨테이너화 및 배포 (FR-1)
*   **FR-1.1:** Frontend 및 Backend 애플리케이션은 Docker 이미지를 통해 컨테이너화되어야 합니다.
*   **FR-1.2:** 각 애플리케이션 컨테이너는 K3s 클러스터 내의 `Deployment` 리소스로 배포되어야 합니다.
*   **FR-1.3:** `Deployment`는 애플리케이션의 고가용성을 위해 최소 2개 이상의 Pod 레플리카를 유지해야 합니다.
*   **FR-1.4:** 각 `Deployment`는 Liveness Probe 및 Readiness Probe를 포함하여 Pod의 생존 여부와 트래픽 수용 가능 여부를 주기적으로 검사해야 합니다.

#### 3.2. 외부 접근 관리 (FR-2)
*   **FR-2.1:** Frontend 및 Backend 서비스는 `Ingress` 리소스를 통해 외부에서 HTTP/HTTPS로 접근 가능해야 합니다.
*   **FR-2.2:** `Ingress`는 URL 경로 기반 라우팅을 지원해야 합니다 (예: `/`는 Frontend, `/api`는 Backend).
*   **FR-2.3:** Ingress는 K3s에 내장된 Traefik Ingress Controller를 활용해야 합니다.
*   **FR-2.4:** (선택 사항) 특정 경우 `NodePort` 타입을 사용하여 서비스에 직접 접근할 수 있도록 구성할 수 있어야 합니다.

#### 3.3. 내부 서비스 통신 (FR-3)
*   **FR-3.1:** 클러스터 내부의 Pod들은 `Service` 이름을 통해 다른 `Service`에 접근할 수 있어야 합니다 (Kubernetes DNS 기반 서비스 디스커버리 활용).
*   **FR-3.2:** `api-gateway` Pod는 `postgresql-service`를 통해 PostgreSQL 데이터베이스에 접근할 수 있어야 합니다.

#### 3.4. 환경 설정 및 비밀 데이터 관리 (FR-4)
*   **FR-4.1:** Frontend 애플리케이션의 외부 API 엔드포인트(`NEXT_PUBLIC_API_URL`)는 `ConfigMap`을 통해 관리되고, 해당 값은 브라우저가 접근할 수 있는 외부 URL(예: `http://localhost:30080` 또는 `http://<도메인>/api`)로 설정되어야 합니다.
*   **FR-4.2:** 데이터베이스 연결 정보, API 키 등 민감한 데이터는 `Secret` 리소스를 통해 안전하게 관리되고, Pod에 환경 변수 또는 파일 형태로 주입되어야 합니다.

#### 3.5. 데이터 지속성 (FR-5)
*   **FR-5.1:** PostgreSQL 데이터베이스는 `PersistentVolumeClaim` (PVC)을 사용하여 데이터의 영구적 저장을 보장해야 합니다.
*   **FR-5.2:** K3s의 기본 `local-path` StorageClass를 사용하여 PVC를 프로비저닝할 수 있어야 합니다. (장기적으로는 AWS EBS CSI 드라이버 등으로 전환 고려)

#### 3.6. CI/CD 파이프라인 자동화 (FR-6)
*   **FR-6.1:** 코드 저장소(Git)에 Push 시, Frontend 및 Backend 애플리케이션의 Docker 이미지를 자동으로 빌드해야 합니다.
*   **FR-6.2:** 빌드된 Docker 이미지는 AWS ECR(Elastic Container Registry)에 자동으로 푸시되어야 합니다.
*   **FR-6.3:** ECR에 푸시된 최신 이미지를 사용하여 Kubernetes `Deployment`를 자동으로 업데이트하고 배포해야 합니다.
*   **FR-6.4:** `ConfigMap` 및 `Secret` 업데이트가 필요할 경우, CI/CD 파이프라인을 통해 배포될 수 있어야 합니다.
*   **FR-6.5:** 배포는 무중단 롤링 업데이트 방식으로 진행되어야 합니다.
*   **FR-6.6:** (선택 사항) AWS CodeBuild, AWS CodePipeline 등 AWS CI/CD 서비스를 활용하여 파이프라인을 구축할 수 있어야 합니다.

---

### 4. 비기능 요구사항 (Non-Functional Requirements - NFRs)

*   **NFR-1. 성능:**
    *   API 응답 시간: 특정 TPS(초당 트랜잭션 수)에서 API 응답 시간 99th percentile이 Xms 이하여야 합니다.
    *   배포 시간: 코드 Push부터 프로덕션 배포 완료까지 Y분 이내로 이루어져야 합니다.
*   **NFR-2. 가용성:**
    *   클러스터 및 애플리케이션 가동 시간: 월간 99.9% 이상을 목표로 합니다.
    *   롤링 업데이트 중 다운타임은 없어야 합니다.
*   **NFR-3. 확장성:**
    *   CPU/메모리 사용량에 따라 Pod가 자동으로 스케일링될 수 있는 기반을 마련해야 합니다. (향후 HPA 도입 고려)
    *   새로운 서비스 추가 시, Kubernetes 매니페스트 및 CI/CD 파이프라인에 쉽게 통합될 수 있어야 합니다.
*   **NFR-4. 보안:**
    *   AWS IAM을 통해 K3s 클러스터 접근 및 관리 권한이 제어되어야 합니다.
    *   Kubernetes RBAC를 통해 클러스터 내 사용자 및 서비스 계정의 권한이 최소 원칙에 따라 관리되어야 합니다.
    *   Secrets는 암호화되어 저장 및 전송되어야 합니다.
*   **NFR-5. 관찰 가능성 (Observability):**
    *   모든 애플리케이션 Pod의 로그는 중앙화된 로깅 시스템(예: AWS CloudWatch Logs)으로 수집되어야 합니다.
    *   클러스터 리소스(CPU, 메모리, 네트워크) 및 애플리케이션 지표(응답 시간, 오류율)에 대한 모니터링 시스템을 구축해야 합니다.
    *   주요 지표 임계치 초과 시 알림 시스템을 통해 담당자에게 통보되어야 합니다.
*   **NFR-6. 유지보수성:**
    *   모든 Kubernetes 매니페스트 및 CI/CD 스크립트는 Git 기반으로 버전 관리되어야 합니다.
    *   환경별(개발/스테이징/프로덕션) 설정은 명확하게 구분되어 관리되어야 합니다.

---

### 5. 기술 스택 및 의존성 (Technical Stack & Dependencies)

*   **클러스터:** K3s (Kubernetes)
*   **클라우드 플랫폼:** AWS EC2
*   **컨테이너 런타임:** Containerd (K3s 기본)
*   **네트워킹:** Flannel (K3s 기본)
*   **Ingress Controller:** Traefik (K3s 내장)
*   **지속성 스토리지:** K3s `local-path` provisioner (초기)
*   **컨테이너 레지스트리:** AWS ECR (Elastic Container Registry)
*   **CI/CD 도구:** AWS CodeCommit, AWS CodeBuild, AWS CodePipeline (또는 Jenkins, GitLab CI/CD, GitHub Actions 등)
*   **명령줄 도구:** `kubectl`
*   **자동화 스크립트:** `.bat` (Windows CI/CD 에이전트), Bash 스크립트 (Linux CI/CD 에이전트)

---

### 6. 성공 기준 (Success Metrics)

*   Frontend 및 Backend 애플리케이션의 AWS 클라우드 K3s 배포 성공률 99% 달성.
*   CI/CD 파이프라인을 통한 배포 시간 10분 이내 달성.
*   클러스터 및 애플리케이션 가동 시간 99.9% 이상 유지.
*   애플리케이션 배포 및 환경 관리에 소요되는 수동 작업 시간 80% 이상 감소.
*   개발팀 및 운영팀의 배포 프로세스 만족도 4점 이상 (5점 척도).

---

### 7. 향후 고려사항 (Future Considerations)

*   **고가용성 마스터:** 단일 마스터 노드 K3s에서 HA(고가용성) K3s 또는 AWS EKS 완전 관리형 서비스로의 전환.
*   **모니터링 심화:** Prometheus, Grafana, ELK Stack 등 전문 모니터링/로깅 솔루션 도입.
*   **보안 강화:** OIDC를 통한 AWS IAM 연동, Pod Security Standards 적용, 네트워크 정책 심화.
*   **비용 최적화:** 스팟 인스턴스 사용, Pod 리소스 사용량 최적화.
*   **백업 및 복구:** etcd 데이터베이스 및 Persistent Volume 데이터의 주기적인 백업 및 복구 전략 수립.
*   **IaC (Infrastructure as Code):** AWS 인프라 자체를 Terraform 또는 CloudFormation으로 관리하여 인프라 구축까지 자동화.
*   **GitOps 도입:** Argo CD 또는 Flux CD를 활용한 선언적 CD 파이프라인 구축.

---