# Use an official Node.js runtime as a parent image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json into the container
COPY package*.json ./
# Install any needed packages
RUN npm install

# Copy the current directory contents into the container at /app
COPY . .

# Add build argument for backend URL
ARG BACKEND_URL
ENV NEXT_PUBLIC_BACKEND_URL=${BACKEND_URL:-http://localhost:8080}

# Build the app
RUN npm run build

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run the app
CMD ["npm", "start"]