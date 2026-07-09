# Stage 1: Build static React files
FROM node:22-slim AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Build argument to inject backend API url during compilation
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Stage 2: Serve using Nginx
FROM nginx:alpine

# Copy compiled assets from Stage 1
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration for port 8080
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
