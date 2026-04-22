FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npx prisma generate

# Paso agregado: Compilar el código de NestJS (TypeScript a JavaScript)
RUN npm run build

EXPOSE 10000

# Comando corregido: Iniciar el servidor en modo producción
CMD ["npm", "run", "start:prod"]