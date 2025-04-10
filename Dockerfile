# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.11
# FROM library/python:${PYTHON_VERSION}-slim-bookworm AS builder

# ARG PYPI_MIRROR=https://pypi.org/simple
# WORKDIR /tmp
# COPY ./pyproject.toml ./uv.lock ./
# RUN <<EOT
#     pip install uv --upgrade --no-cache-dir -i ${PYPI_MIRROR}
#     uv export --no-dev -o requirements.txt
# EOT


FROM library/python:${PYTHON_VERSION}-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

# ARG PYPI_MIRROR=https://pypi.org/simple
# COPY --from=builder /tmp/requirements.txt /tmp/requirements.txt
# RUN pip install --upgrade --no-cache-dir -i ${PYPI_MIRROR} -r /tmp/requirements.txt

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

ARG PYPI_MIRROR=https://pypi.org/simple

RUN <<EOT
    pip install --upgrade --no-cache-dir -i ${PYPI_MIRROR} -r ./requirements/base.txt
    chmod +x entrypoint.sh
EOT

ENTRYPOINT [ "bash", "./entrypoint.sh" ]
