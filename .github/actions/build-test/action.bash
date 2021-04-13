#!/usr/bin/env bash

: "${IMAGE_NAME:=dotctl-test}"
: "${IMAGE_TAG:=latest}"

docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
