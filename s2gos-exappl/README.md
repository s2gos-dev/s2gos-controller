# DTE-S2GOS example application

Build and run the image

```commandline
cd ..
docker build -f s2gos-exappl/Dockerfile -t s2gos-exappl-v1 .
docker run s2gos-exappl-v1 s2gos-exappl --help
docker run -it s2gos-exappl-v1 /bin/bash
```
