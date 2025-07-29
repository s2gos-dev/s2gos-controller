# Stage 1 ---------------------------
FROM ghcr.io/prefix-dev/pixi:0.23.0 AS build

WORKDIR /app
COPY . .
RUN pixi install --locked -e production
RUN pixi shell-hook -e production -s bash > /shell-hook
RUN echo "#!/bin/bash" > /app/entrypoint.sh
RUN cat /shell-hook >> /app/entrypoint.sh
RUN echo 'exec "$@"' >> /app/entrypoint.sh

# Stage 2 ---------------------------
FROM ubuntu:24.04 AS production
WORKDIR /app
COPY --from=build /app/.pixi/envs/production /app/.pixi/envs/production
COPY --from=build --chmod=0755 /app/entrypoint.sh /app/entrypoint.sh
#COPY ./my_project /app/my_project

ENTRYPOINT [ "/app/entrypoint.sh" ]
