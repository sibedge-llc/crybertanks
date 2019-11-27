FROM golang:alpine as builder
WORKDIR /go/src/signalr
COPY . .
RUN GO111MODULE=on GOFLAGS=-mod=vendor CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags="-w -s" -o signalr main.go

FROM scratch
COPY --from=builder /go/src/signalr/signalr /go/bin/cybertank
ENTRYPOINT ["/go/bin/cybertank"]