FROM node:20-alpine

# Instrucción agregada para instalar la librería necesaria para Prisma
RUN apk add --no-cache openssl

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npx prisma generate

RUN npm run build

EXPOSE 10000

CMD ["npm", "run", "start:prod"]