#!/usr/bin/env bash
#
# Build (and optionally push) the s2gos-server image.
#
# By default the eozilla packages (gavicore, procodile, wraptile) are pinned
# to EOZILLA_VERSION.
#
# Usage:
#   ./s2gos-server/build-image.sh                    # build, tag from s2gos-server version
#   ./s2gos-server/build-image.sh -t dev             # build with an explicit tag
#   ./s2gos-server/build-image.sh -t 0.1.0 --push    # build and push to the registry
#
#   # Build against a specific eozilla version:
#   ./s2gos-server/build-image.sh --eozilla-version 0.2.0.dev1
#
#   # Override a single package spec (e.g. use the newest proper release):
#   ./s2gos-server/build-image.sh --wraptile wraptile --stable
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

IMAGE_REPO="${IMAGE_REPO:-quay.io/s2gos/s2gos-server}"
IMAGE_TAG=""
PUSH=0
EOZILLA_VERSION="0.2.0.dev1"
GAVICORE_SPEC=""
PROCODILE_SPEC=""
WRAPTILE_SPEC=""
PRE_FLAG="--pre"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -t|--tag)          IMAGE_TAG="$2"; shift 2 ;;
    -r|--repo)         IMAGE_REPO="$2"; shift 2 ;;
    --eozilla-version) EOZILLA_VERSION="$2"; shift 2 ;;
    --gavicore)        GAVICORE_SPEC="$2"; shift 2 ;;
    --procodile)       PROCODILE_SPEC="$2"; shift 2 ;;
    --wraptile)        WRAPTILE_SPEC="$2"; shift 2 ;;
    --pre)             PRE_FLAG="--pre"; shift ;;
    --stable|--no-pre) PRE_FLAG=""; shift ;;
    --push)            PUSH=1; shift ;;
    -h|--help)         sed -n '2,21p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *)                 echo "unknown argument: $1" >&2; exit 1 ;;
  esac
done

# Default each unset package spec to the pinned eozilla version.
GAVICORE_SPEC="${GAVICORE_SPEC:-gavicore==${EOZILLA_VERSION}}"
PROCODILE_SPEC="${PROCODILE_SPEC:-procodile==${EOZILLA_VERSION}}"
WRAPTILE_SPEC="${WRAPTILE_SPEC:-wraptile==${EOZILLA_VERSION}}"

# Default the tag to the version declared in s2gos-server/pyproject.toml.
if [[ -z "$IMAGE_TAG" ]]; then
  IMAGE_TAG="$(grep -m1 '^version = ' "$SCRIPT_DIR/pyproject.toml" | cut -d'"' -f2)"
fi

IMAGE="${IMAGE_REPO}:${IMAGE_TAG}"
echo "Building ${IMAGE} (context: ${SCRIPT_DIR}, eozilla: ${EOZILLA_VERSION})"

docker build \
  -f "$SCRIPT_DIR/Dockerfile" \
  --build-arg "GAVICORE_SPEC=${GAVICORE_SPEC}" \
  --build-arg "PROCODILE_SPEC=${PROCODILE_SPEC}" \
  --build-arg "WRAPTILE_SPEC=${WRAPTILE_SPEC}" \
  --build-arg "PRE_FLAG=${PRE_FLAG}" \
  -t "$IMAGE" \
  "$SCRIPT_DIR"

echo "Built ${IMAGE}"

if [[ "$PUSH" -eq 1 ]]; then
  echo "Pushing ${IMAGE}"
  docker push "$IMAGE"
fi
