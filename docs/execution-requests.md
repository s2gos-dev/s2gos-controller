# Execution Requests

For larger or complex sets of input parameters it is recommended to use a 
_execution request file_ in JSON or YAML format. The structure is simple, for example:

```json
{
    "process_id": "primes_between",
    "inputs": {
      "min_val": 10,
      "max_val": 80
    }
}
```

This is the CLI's execution-request format. Python's `ProcessRequest` contains
`inputs`, `outputs`, and `subscriber`; pass the process ID separately to
`client.execute_process(process_id, request=...)`. The `dotpath` setting is a
CLI convenience for constructing nested inputs, not a process input itself.

Use `s2gos-client create-request PROCESS_ID` to generate a starting template from
the server's process description. Review generated values before use.
`s2gos-client validate-request --request request.json` validates the request
structure offline; it does not validate inputs against a remote process schema.
See the [CLI walkthrough](guide/client-cli.md) for a complete submission.

The execution-request file format in detail:

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
