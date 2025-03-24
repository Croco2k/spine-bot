# syntax=docker/dockerfile:1
FROM golang:1.24 as builder

WORKDIR /app

COPY go.mod ./
COPY go.sum ./
RUN go mod download

COPY . ./
RUN go build -o main .

FROM gcr.io/distroless/base-debian11
WORKDIR /app
COPY --from=builder /app/main /app/
CMD ["/app/main"]
