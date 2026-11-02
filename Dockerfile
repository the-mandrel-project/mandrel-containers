# syntax=docker/dockerfile:1

ARG GO_VERSION=1.26
ARG CLI_REPO=https://gitlab.com/the-mandrel-project/mandrel-cli.git
ARG CLI_REF=main
ARG KONG_REPO=https://gitlab.com/the-mandrel-project/mandrel-plugin-kong.git
ARG KONG_REF=main
ARG GO_REPO=https://gitlab.com/the-mandrel-project/mandrel-go.git
ARG GO_REF=main

# ==============================================================================
# Stage 1: Build Core CLI and Plugins from Source
# ==============================================================================
FROM golang:${GO_VERSION}-alpine AS builder

RUN apk add --no-cache git ca-certificates

WORKDIR /workspace

# Clone dependencies as siblings so local replace directives in plugin go.mod resolve cleanly
ARG CLI_REPO
ARG CLI_REF
RUN git clone --depth 1 --branch ${CLI_REF} ${CLI_REPO} /workspace/mandrel-cli

ARG GO_REPO
ARG GO_REF
RUN git clone --depth 1 --branch ${GO_REF} ${GO_REPO} /workspace/mandrel-go

ARG KONG_REPO
ARG KONG_REF
RUN git clone --depth 1 --branch ${KONG_REF} ${KONG_REPO} /workspace/mandrel-plugin-kong

# Build mandrel-cli
WORKDIR /workspace/mandrel-cli
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/mandrel ./cmd/mandrel-cli && \
    cp /out/mandrel /out/mandrel-cli

# Build mandrel-plugin-kong (mandrel-generator-kong)
WORKDIR /workspace/mandrel-plugin-kong
RUN go mod tidy && \
    CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/mandrel-generator-kong main.go

# ==============================================================================
# Stage 2: Minimal Zero-Dependency Distroless Runtime
# ==============================================================================
FROM gcr.io/distroless/static-debian12:nonroot

LABEL org.opencontainers.image.title="Mandrel CLI" \
      org.opencontainers.image.description="Minimal zero-dependency container for Mandrel CLI and official governance plugins" \
      org.opencontainers.image.source="https://gitlab.com/the-mandrel-project/mandrel-containers" \
      org.opencontainers.image.licenses="Apache-2.0"

# Copy CLI binary and symlink
COPY --from=builder /out/mandrel /usr/local/bin/mandrel
COPY --from=builder /out/mandrel-cli /usr/local/bin/mandrel-cli

# Copy official plugins
COPY --from=builder /out/mandrel-generator-kong /usr/local/bin/mandrel-generator-kong

USER nonroot:nonroot
WORKDIR /workspace

ENTRYPOINT ["/usr/local/bin/mandrel"]
CMD ["--help"]
