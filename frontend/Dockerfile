# Multi-stage build for production optimization
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Build the application with environment variable
ARG REACT_APP_API_URL=http://localhost:8001/api/v1
ENV REACT_APP_API_URL=$REACT_APP_API_URL

RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built React app from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration for React Router
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 3000

# Start nginx
CMD ["nginx", "-g", "daemon off;"]