# weather/Dockerfile
FROM node:20-alpine
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY . .
ENV PORT=8081
EXPOSE 8081
CMD ["node", "server.js"]
