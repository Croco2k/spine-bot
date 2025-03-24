FROM golang:1.24 AS builder

WORKDIR /app
COPY go.mod ./
COPY go.sum ./
RUN go mod download

COPY . ./
RUN go build -o main .

# Используем slim-образ с glibc >= 2.34
FROM debian:bullseye-slim

WORKDIR /app
COPY --from=builder /app/main .

# Устанавливаем libc6, если нужно
RUN apt-get update && apt-get install -y libc6 && apt-get clean

CMD ["./main"]
