#!/usr/bin/env bash
# Recipes for copying individually; running this file does not submit jobs.
exit 0

# --8<-- [start:server]
s2gos-server run -- wraptile.services.local.testing:service
# --8<-- [end:server]

# --8<-- [start:configure]
s2gos-client configure --api-url http://127.0.0.1:8008 --auth-type none --config local-client.yaml
# --8<-- [end:configure]

# --8<-- [start:inspect]
s2gos-client list-processes --config local-client.yaml
s2gos-client get-process primes_between --config local-client.yaml
# --8<-- [end:inspect]

# --8<-- [start:template]
s2gos-client create-request primes_between --format json --config local-client.yaml
# --8<-- [end:template]

# --8<-- [start:validate]
s2gos-client validate-request --request examples/guides/primes-request.json
# --8<-- [end:validate]

# --8<-- [start:submit]
s2gos-client execute-process --request examples/guides/primes-request.json --config local-client.yaml
# --8<-- [end:submit]

# --8<-- [start:inputs]
s2gos-client execute-process primes_between -i min_val=10 -i max_val=80 --config local-client.yaml
# --8<-- [end:inputs]

# --8<-- [start:jobs]
s2gos-client list-jobs --config local-client.yaml
s2gos-client get-job YOUR_JOB_ID --config local-client.yaml
# --8<-- [end:jobs]

# --8<-- [start:results]
s2gos-client get-job-results YOUR_JOB_ID --config local-client.yaml
# --8<-- [end:results]

# --8<-- [start:dismiss]
s2gos-client dismiss-job YOUR_JOB_ID --config local-client.yaml
# --8<-- [end:dismiss]

# --8<-- [start:app]
s2gos-client show-app --config local-client.yaml
# --8<-- [end:app]
