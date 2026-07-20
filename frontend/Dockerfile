# Multi-stage production container setup for AegisAI Next.js Frontend
FROM node:18-alpine AS builder

WORKDIR /app

# Copy dependency configs
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm ci

# Copy frontend source code and compile production assets
COPY frontend/ ./
RUN npm run build

# Runtime runner stage
FROM node:18-alpine AS runner

WORKDIR /app/frontend

# Copy compiled build artifacts and dependencies
COPY --from=builder /app/frontend/package*.json ./
COPY --from=builder /app/frontend/.next ./.next
COPY --from=builder /app/frontend/public ./public
COPY --from=builder /app/frontend/node_modules ./node_modules

# Expose Next.js default server port
EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["npm", "start"]
