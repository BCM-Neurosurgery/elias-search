FROM alpine:3.20

# Install necessary packages
RUN apk add --no-cache \
    curl \
    docker-cli \
    bash

# Set working directory
WORKDIR /app

# Copy and set permissions for the watchdog script
COPY watchdog.sh .
RUN chmod +x watchdog.sh

# Use bash for better error handling
CMD ["./watchdog.sh"]