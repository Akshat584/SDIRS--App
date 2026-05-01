# Stage 1: Build React App
FROM node:18-alpine as build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy project
COPY . .

# Build the app
RUN npm run build

# Stage 2: Serve with Nginx (optional if using main nginx)
# In our monorepo, we'll use a single Nginx for both, 
# but having a standalone frontend image is good for modularity.
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
