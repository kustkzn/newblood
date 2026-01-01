# Dockerfile
FROM golang:1.22-alpine AS builder

WORKDIR /app

# Копируем ВЕСЬ backend (включая go.mod, go.sum, исходники)
COPY src/backend/ ./backend/

WORKDIR /app/backend

# НЕ вызываем go mod init — он уже есть!
RUN go mod tidy && \
    CGO_ENABLED=0 GOOS=linux go build -o /app/main .

# Финальный образ
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

COPY --from=builder /app/main .

# Копируем frontend из src/frontend/
COPY src/frontend/ /root/frontend/

EXPOSE 8080

CMD ["./main"]