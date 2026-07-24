#  Copyright (c) 2025-2026 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.
#
# Image for the S2GOS gateway server (s2gos-server).
#
# The eozilla packages (gavicore, procodile, wraptile) are pulled from
# PyPI, so the build context is just this directory:
#
#   docker build -t quay.io/s2gos/s2gos-server:dev s2gos-server/
#
# By default the eozilla packages are pinned to the version in EOZILLA_VERSION.
# Override it to build against another eozilla version:
#
#   docker build --build-arg EOZILLA_VERSION=0.2.0.dev1 \
#     -t quay.io/s2gos/s2gos-server:0.2.0.dev1 s2gos-server/
#
# For non-pinned resolution, override the *_SPEC args with bare names. PRE_FLAG
# then controls whether pre-releases are considered (--pre, the default) or only
# proper releases (empty):
#
#   # Newest proper release only:
#   docker build \
#     --build-arg GAVICORE_SPEC=gavicore \
#     --build-arg PROCODILE_SPEC=procodile \
#     --build-arg WRAPTILE_SPEC=wraptile \
#     --build-arg PRE_FLAG= -t quay.io/s2gos/s2gos-server:0.1.2 s2gos-server/

FROM python:3.12-slim AS production

WORKDIR /app

# s2gos-server 0.1.0 does not ship its own Airflow service, so we default to
# wraptile's generic Airflow service. It needs the Airflow connection details at
# run time, e.g.:
#   docker run … s2gos-server run -- wraptile.services.airflow:service \
#     --airflow-base-url=… --airflow-username=… --airflow-password=…
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    EOZILLA_SERVER_HOST=0.0.0.0 \
    EOZILLA_SERVER_PORT=8008 \
    EOZILLA_SERVICE="wraptile.services.airflow:service"

# Eozilla version the packages are pinned to by default (a dev release).
ARG EOZILLA_VERSION=0.2.0.dev1
# Eozilla package specs. Default to the pinned EOZILLA_VERSION; override with
# bare names ("gavicore") for non-pinned resolution, or other "name==X.Y.Z"
# pins. An explicit "==<dev>" pin installs even without PRE_FLAG.
ARG GAVICORE_SPEC=gavicore==${EOZILLA_VERSION}
ARG PROCODILE_SPEC=procodile==${EOZILLA_VERSION}
ARG WRAPTILE_SPEC=wraptile==${EOZILLA_VERSION}
# "--pre" accepts pre-releases and proper releases (newest wins); only relevant
# for bare-name specs. Set empty to restrict those to proper releases only.
ARG PRE_FLAG=--pre

COPY . /app/s2gos-server

RUN pip install --no-cache-dir --upgrade pip \
    # Airflow client is only on PyPI and is not a hard dep of s2gos-server.
    && pip install --no-cache-dir apache-airflow-client==3.0.2 requests \
    # Install eozilla releases first; PRE_FLAG is scoped to just these packages
    # so pre-releases of other deps are not pulled in.
    && pip install --no-cache-dir ${PRE_FLAG} "${GAVICORE_SPEC}" "${PROCODILE_SPEC}" "${WRAPTILE_SPEC}" \
    # Install s2gos-server itself; its eozilla requirements are already
    # satisfied by the dev releases above, so pip leaves them in place.
    && pip install --no-cache-dir /app/s2gos-server

EXPOSE 8008

CMD ["s2gos-server", "run"]
