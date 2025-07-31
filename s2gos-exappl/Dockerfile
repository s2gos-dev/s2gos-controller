# Stage 1 ---------------------------
FROM ghcr.io/prefix-dev/pixi:0.50.2-bookworm-slim AS build
WORKDIR /app
RUN mkdir s2gos-common
RUN mkdir s2gos-exappl
COPY ./s2gos-common ./s2gos-common
COPY ./s2gos-exappl ./s2gos-exappl
RUN cd ./s2gos-exappl && pixi install --locked -e production
RUN cd ./s2gos-exappl && pixi shell-hook -e production -s bash > /shell-hook
RUN echo "#!/bin/bash" > /app/entrypoint.sh
RUN cat /shell-hook >> /app/entrypoint.sh
RUN echo 'exec "$@"' >> /app/entrypoint.sh

# Stage 2 ---------------------------
FROM ubuntu:24.04 AS production
WORKDIR /app
COPY --from=build /app/s2gos-exappl/.pixi/envs/production /app/s2gos-exappl/.pixi/envs/production
COPY --from=build /app/s2gos-common/src /app/s2gos-common/src
COPY --from=build /app/s2gos-exappl/src /app/s2gos-exappl/src
COPY --from=build --chmod=0755 /app/entrypoint.sh /app/entrypoint.sh
ENTRYPOINT [ "/app/entrypoint.sh" ]
