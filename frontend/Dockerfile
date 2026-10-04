FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN chown -R node:node /app
USER node
EXPOSE 5173
# Refresh the persistent dependency volume when the lockfile changes.
CMD ["sh", "-c", "npm ci && npm run dev"]
