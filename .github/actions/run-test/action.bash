#!/usr/bin/env bash

: "${ROOT_DIR:?must be set}"
: "${IMAGE_NAME:?must be set}"
: "${IMAGE_TAG:?must be set}"
: "${PYTEST_CACHE_DIR:=.pytest_cache}"

assertDirectory() {
  : "${1:?directory must be provided}"
  if [ ! -d "$1" ]; then
    echo "'$1' directory does not exist"
    exit 1
  fi
}

assertFile() {
  : "${1:?file must be provided}"
  if [ ! -f "$1" ]; then
    echo "'$1' file does not exist"
    exit 1
  fi
}

ROOT_DIR=$(realpath "${ROOT_DIR}")
PYTEST_CACHE_DIR=$(realpath "${PYTEST_CACHE_DIR}")

assertDirectory "${ROOT_DIR}"
assertDirectory "${ROOT_DIR}/src"
assertDirectory "${ROOT_DIR}/tests"
assertFile "${ROOT_DIR}/.env"
assertFile "${ROOT_DIR}/.env.test"

mkdir -p "${PYTEST_CACHE_DIR}"
touch "${ROOT_DIR}/coverage.xml"
touch "${ROOT_DIR}/test-report.xml"

docker run \
  --rm \
  -v "${PYTEST_CACHE_DIR}":/home/dotctl/.pytest_cache \
  -v "${ROOT_DIR}"/.env:/home/dotctl/.env \
  -v "${ROOT_DIR}"/.env.test:/home/dotctl/.env.test \
  -v "${ROOT_DIR}"/src:/home/dotctl/src \
  -v "${ROOT_DIR}"/tests:/home/dotctl/tests \
  -v "${ROOT_DIR}"/coverage.xml:/home/dotctl/coverage.xml \
  -v "${ROOT_DIR}"/test-report.xml:/home/dotctl/test-report.xml \
  "${IMAGE_NAME}":"${IMAGE_TAG}" \
  pipenv run coverage

echo "::set-output name=test-report-file::${ROOT_DIR}/test-report.xml"
echo "::set-output name=coverage-file::${ROOT_DIR}/coverage.xml"
