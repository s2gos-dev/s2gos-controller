# Client API Reference

The entrypoint of the S2GOS client API is the `s2gos_client.Client` class that 
provides a synchronous API for interacting with the S2GOS processing service.
If you want an asynchronous version, use the `AsyncClient` class instead.
It provides the same interface, but using asynchronous server calls.

Both clients return their configuration as a `s2gos_client.ClientConfig` object.

Methods of the `s2gos_client.Client` and `s2gos_client.AsyncClient` 
may raise a `s2gos_client.ClientError` if a server call fails. 

The S2GOS client API is a thin wrapper around the 
[Eozilla](https://eo-tools.github.io/eozilla/) Client API 
called [Cuiman](https://eo-tools.github.io/eozilla/client-api/).
