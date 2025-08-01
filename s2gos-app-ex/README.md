# DTE-S2GOS application example

Build and run the image

```commandline
cd ..
docker build -f s2gos-app-ex/Dockerfile -t s2gos-app-ex-v1 .
docker run s2gos-app-ex-v1 s2gos-app-ex --help
docker run -it s2gos-app-ex-v1 /bin/bash
```
