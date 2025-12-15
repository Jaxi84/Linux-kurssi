
FROM node:20-alpine
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm ci --omit=dev
COPYCOPY . .
ENV PORT=8080
EXPOSE 8080

