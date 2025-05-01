# Node 20 버전의 가벼운 이미지 사용
FROM node:20-slim

# 컨테이너 작업 디렉토리 생성
WORKDIR /app

# package.json과 package-lock.json 복사
COPY package*.json ./

# 의존성 설치
RUN npm install

# 전체 프로젝트 복사
COPY . .

EXPOSE 3000
# Vite dev 서버 실행 (모든 외부 요청 허용)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"] 