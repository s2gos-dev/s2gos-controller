# Client API Reference

The S2GOS client API is a thin wrapper around the 
[Eozilla](https://eo-tools.github.io/eozilla/) Client API 
called [Cuiman](https://eo-tools.github.io/eozilla/cuiman/) that
is provided by the Python package `s2gos_client`.

The entrypoint of the S2GOS client API is the `create_client` function. 
It creates an instance of the 
[`Client`](https://eo-tools.github.io/eozilla/cuiman/api/#cuiman.Client) class that 
provides a synchronous API for interacting with the S2GOS processing service.

If you want an asynchronous client, use the `create_async_client` function instead.
It creates an instance of 
[`AsyncClient`](https://eo-tools.github.io/eozilla/cuiman/api/#cuiman.AsyncClient) with 
the same interface, but using asynchronous server calls.

Both clients return their configuration as a 
[`ClientConfig`](https://eo-tools.github.io/eozilla/cuiman/api/#cuiman.ClientConfig) 
object.

Methods of the `Client` and `AsyncClient` may raise a 
[`s2gos_client.ClientError`](https://eo-tools.github.io/eozilla/cuiman/api/#cuiman.ClientError) 
if a server call fails. 


::: s2gos_client.create_client

::: s2gos_client.create_async_client

