# Client API Reference

The [`Client`](#s2gos_client.Client) class provides a synchronous API.
If you want an asynchronous version, use the `AsyncClient` class instead.
It provides the same interface, but using asynchronous server calls.

Both clients return their configuration as a 
[`ClientConfig`](#s2gos_client.ClientConfig) object.

Methods of the [`Client`](#s2gos_client.Client) and `AsyncClient` 
may raise a [`ClientException`](#s2gos_client.ClientError) if a server call fails. 

::: s2gos_client.Client

::: s2gos_client.ClientConfig

::: s2gos_client.ClientException
