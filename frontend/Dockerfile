FROM node:20-alpine

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Expose Vite default port
EXPOSE 5173

# Start the development server
CMD ["npm", "run", "dev", "--", "--host"]
