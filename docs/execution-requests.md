# Execution Requests

For larger or complex sets of input parameters it is recommended to use a 
_execution request file_ in JSON or YAML format. The structure is simple, for example:

```json
{
    "process_id": "primes_between",
    "inputs": {
      "min_val": 100,
      "max_val": 200
    }
}
```

The process request file format in detail:

- `process_id`: Process identifier
- `dotpath`: Whether dots in input names should be used to create
    nested object values. Defaults to `False`.
- `inputs`: Optional process inputs given as key-value mapping.
    Values may be of any JSON-serializable type accepted by
    the given process.
- `outputs`: Optional process outputs given as key-value mapping.
    Values are of type [Output](https://app.swaggerhub.com/apis/OGC/ogcapi-processes-1-example-1/1.0.0#/output)
    and should be supported by the given process.
- `subscriber`: Optional object comprising callback
    URLs that are informed about process status changes
    while the processing takes place. The URLs are `successUri`,
    `inProgressUri`, and `failedUri` and none is required.
    See also [Subscriber](https://app.swaggerhub.com/apis/OGC/ogcapi-processes-1-example-1/1.0.0#/subscriber).
