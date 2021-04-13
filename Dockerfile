# syntax = docker/dockerfile:experimental
FROM python:3.9-alpine3.14 AS builder

RUN apk update && apk add --no-cache \
  build-base \
  rust \
  cargo \
  libffi-dev \
  openssl-dev \
  ;

# cache pip packages and cargo to speed up native code builds
RUN \
  --mount=type=cache,target=/root/.cache/pip \
  --mount=type=cache,target=/root/.cargo \
  pip install \
  pipenv \
  setuptools \
  cryptography \
  ;

FROM python:3.9-alpine3.14 AS runner

COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/local/lib/python3.9 /usr/local/lib/python3.9

RUN apk add --no-cache sudo

RUN addgroup -g 10001 dotctl
RUN adduser -D -u 10001 -G dotctl dotctl
RUN mkdir -p /etc/sudoers.d \
  && echo "dotctl ALL=(ALL:ALL) NOPASSWD:SETENV: ALL" > /etc/sudoers.d/dotctl

USER dotctl
WORKDIR /home/dotctl
RUN mkdir -p .venv && mkdir -p .cache/pipenv

COPY --chown=dotctl:dotctl Pipfile Pipfile.lock ./
COPY --chown=dotctl:dotctl src/dotctl/__init__.py src/dotctl/__init__.py
COPY --chown=dotctl:dotctl setup.py pyproject.toml README.md ./
RUN pipenv --bare install -d --deploy \
  && rm -rf /home/dotctl/.cache/pipenv/* \
  && rm -rf /home/dotctl/.local  \
  && find /tmp -user dotctl -group dotctl -delete

CMD [ "pipenv", "scripts" ]
