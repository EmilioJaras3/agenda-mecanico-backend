FROM node:20-alpine

# InstrucciÃ³n agregada para instalar la librerÃ­a necesaria para Prisma
RUN apk add --no-cache openssl

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npx prisma generate

RUN npm run build

EXPOSE 10000

CMD ["sh", "-c", "npx prisma db push --skip-generate && npm run start:prod"]
