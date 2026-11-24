# ── Build Stage ───────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency manifests
COPY package*.json ./

# Install packages
RUN npm ci --legacy-peer-deps

# Copy frontend source files
COPY . .

# Receive environment variables at build-time
ARG VITE_API_BASE_URL
ARG VITE_APP_NAME
ARG VITE_POWERBI_CLIENT_ID

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_APP_NAME=$VITE_APP_NAME \
    VITE_POWERBI_CLIENT_ID=$VITE_POWERBI_CLIENT_ID

# Build React production bundle
RUN npm run build


# ── Development Stage ─────────────────────────────────────────────────────────
FROM node:20-alpine AS development

WORKDIR /app

COPY package*.json ./
RUN npm install --legacy-peer-deps

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]


# ── Production Stage (Nginx serving built bundle) ─────────────────────────────
FROM nginx:alpine AS production

# Remove default static files
RUN rm -rf /usr/share/nginx/html/*

# Copy built bundle from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx routing config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
