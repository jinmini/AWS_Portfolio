# Stage 1: 의존성 설치 및 빌드
FROM node:18-alpine AS builder

WORKDIR /app

# 의존성 파일 복사
COPY package*.json ./

# 의존성 설치
RUN npm ci

# 소스 코드 복사
COPY . .

# 빌드 실행
RUN npm run build

# Stage 2: 프로덕션 런타임
FROM node:18-alpine AS runner

WORKDIR /app

# 프로덕션용 사용자 생성
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# 빌드 결과물 복사
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# 사용자 변경
USER nextjs

# 포트 노출
EXPOSE 3000

# 환경 변수
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# 애플리케이션 시작
CMD ["npm", "start"]
