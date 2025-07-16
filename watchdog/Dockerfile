FROM alpine:3.20
RUN apk add --no-cache curl docker-cli
WORKDIR /app
COPY watchdog.sh .
RUN chmod +x watchdog.sh
CMD ["./watchdog.sh"]