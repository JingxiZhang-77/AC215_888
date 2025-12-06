# Use Node.js 18 Alpine for smaller image size
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install bash for shell scripts
RUN apk add --no-cache bash

# Expose port
EXPOSE 3001

# Keep container running for development
CMD ["/bin/bash"]
