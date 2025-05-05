FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm install --legacy-peer-deps

COPY . .

RUN npm run build


CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "<원하는 포트번호>"]