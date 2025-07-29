# ---------- Stage 1: Build with pixi ----------
FROM condaforge/mambaforge as builder

WORKDIR /app

# Install pixi
RUN pip install pixi

# Copy only necessary files
COPY pixi.lock pyproject.toml ./
COPY src ./src

# Install only runtime dependencies (no dev tools)
RUN pixi install --no-dev

# Pack the environment
RUN pixi run conda-pack -o /env.tar.gz

# ---------- Stage 2: Minimal Runtime Image ----------
FROM debian:bullseye-slim

# Install OS-level runtime deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        libglib2.0-0 \
        libxext6 \
        libsm6 \
        libxrender1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Unpack the conda environment
COPY --from=builder /env.tar.gz /env.tar.gz
RUN mkdir -p /opt/conda && \
    tar -xzf /env.tar.gz -C /opt/conda && \
    /opt/conda/bin/conda-unpack

# Set environment paths
ENV PATH="/opt/conda/bin:$PATH"
WORKDIR /app

# Copy source code (optional here — already baked into the env)
# COPY src ./src

# Use the CLI script name defined in pyproject.toml
ENTRYPOINT ["s2gos-exappl"]
