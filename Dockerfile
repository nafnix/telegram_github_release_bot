# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.11
FROM ghcr.io/astral-sh/uv:0.6.14 AS uv
FROM library/python:${PYTHON_VERSION}-slim-bookworm AS builder

# Enable bytecode compilation, to improve cold-start performance.
ENV UV_COMPILE_BYTECODE=1

# Disable installer metadata, to create a deterministic layer.
ENV UV_NO_INSTALLER_METADATA=1

# Enable copy mode to support bind mount caching.
ENV UV_LINK_MODE=copy

# Bundle the dependencies into the Lambda task root via `uv pip install --target`.
#
# Omit any local packages (`--no-emit-workspace`) and development dependencies (`--no-dev`).
# This ensures that the Docker layer cache is only invalidated when the `pyproject.toml` or `uv.lock`
# files change, but remains robust to changes in the application code.
RUN --mount=from=uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv export --frozen --no-emit-workspace --no-dev --no-editable -o requirements.txt && \
    uv pip install -r requirements.txt --target output

FROM library/python:${PYTHON_VERSION}-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

ARG USER=app
ENV BASE_DIR=/app


COPY . ${BASE_DIR}
RUN <<EOT
    useradd -m -d ${BASE_DIR} -s /usr/bin/sh ${USER}
    mkdir -p ${BASE_DIR}
    chown -R ${USER}:${USER} ${BASE_DIR}
EOT

USER ${USER}
WORKDIR ${BASE_DIR}

COPY --from=builder /output ./packages

RUN <<EOT
    chmod +x entrypoint.sh
EOT

ENV PYTHONPATH="${BASE_DIR}/packages:$PYTHONPATH" \
    PATH="${BASE_DIR}/packages/bin:$PATH"

ENTRYPOINT [ "bash", "./entrypoint.sh" ]

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "src.main:app"]
