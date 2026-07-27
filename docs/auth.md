# Authentication

The S2GOS client authenticates requests to the S2GOS service (an
OGC API - Processes server) using standard HTTP mechanisms. There is **no
provider-specific code**: the client speaks generic OAuth2 / OIDC and HTTP
auth, so it works with any compliant authorization server: Keycloak, Auth0,
Azure AD, or a plain token issuer.

This page explains how to configure the client, with a focus on connecting it
to an **OAuth2 authorization server**.

## Supported authentication types

The `auth_type` setting selects how the client authenticates:

| `auth_type` | How it works | Required settings |
|-------------|--------------|-------------------|
| `none`      | No authentication. | — |
| `login`     | OAuth2 *password grant*: exchange username/password for access and refresh tokens, then send the access token as a bearer. | `auth_url`, `username`, `password` (+ `client_id`, `client_secret` if required) |
| `token`     | Send a pre-obtained static token. | `token` |
| `api-key`   | Send an API key in a custom header. | `api_key` |
| `basic`     | HTTP Basic Auth. | `username`, `password` |

For an OAuth2 server you normally use **`login`** (to obtain a token from your
credentials) or **`token`** (if you already hold an access token).

## Configuration settings

The relevant settings (fields of the client configuration) are:

| Setting | Description |
|---------|-------------|
| `api_url` | URL of the S2GOS service (OGC API - Processes). |
| `auth_type` | One of the types above. |
| `auth_url` | The OAuth2 **token endpoint** of your authorization server. |
| `username` / `password` | User credentials for the password grant. |
| `client_id` / `client_secret` | OAuth2 client credentials. `client_secret` is only needed for *confidential* clients. |
| `grant_type` | OAuth2 grant type. Defaults to `password`. |
| `token` | Access token. It may be supplied directly for `auth_type="token"` or retained after a `login`. |
| `refresh_token` | OAuth2 refresh token retained after a `login` when the authorization server returns one. |
| `use_bearer` | If `true` (default), the token is sent as `Authorization: Bearer <token>`. If `false`, it is sent in `token_header`. |
| `token_header` | Header name used when `use_bearer` is `false`. Defaults to `X-Auth-Token`. |
| `api_key` / `api_key_header` | API key and its header (default `X-API-Key`) for `auth_type="api-key"`. |

### Where settings come from

Settings are merged from several sources, in increasing order of precedence:

1. Built-in defaults.
2. The configuration file `~/.s2gos-client` (YAML).
3. Environment variables prefixed with `S2GOS_` (and a local `.env` file).
4. Values passed directly in Python (`create_client(**settings)`).

So a value passed in code overrides an environment variable, which overrides
the config file.

### Default configuration

Out of the box, the client is preconfigured for the hosted S2GOS service and
its Keycloak realm, so a plain `create_client()` targets that deployment. The
built-in defaults are:

| Setting | Default |
|---------|---------|
| `api_url` | `https://s2gos.wraptile.brockmann-consult.de/` |
| `auth_type` | `login` |
| `auth_url` | `https://kc.dev.brockmann-consult.de/realms/eozilla-auth/protocol/openid-connect/token` |
| `client_id` | `cuiman` |
| `grant_type` | `password` |
| `use_bearer` | `true` |

Because `auth_type` defaults to `login`, you still need to supply your
`username` and `password` (via any of the sources above) for the initial token
exchange. Override any default by passing it to `create_client`, setting the
matching `S2GOS_*` environment variable, or storing it in `~/.s2gos-client` —
for example, point `api_url` / `auth_url` at a different deployment.

## Connecting to an OAuth2 server

### 1. Gather your authorization-server details

You need, from your OAuth2 / OIDC provider:

- the **token endpoint** URL → `auth_url`
- a **client ID** (and **client secret** if the client is confidential)
- **user credentials** (username / password)

For a **Keycloak** realm, the token endpoint looks like:

```
https://<keycloak-host>/realms/<realm>/protocol/openid-connect/token
```

### 2. Log in from Python

The recommended way to use the password grant is to pass the settings to
`create_client`. When `auth_type="login"` and no access token is already
configured, the client performs the token exchange immediately. It then uses
the resulting access token as a bearer token on every request:

```python
import os
from s2gos_client import create_client

client = create_client(
    api_url="https://s2gos.example/",
    auth_type="login",
    auth_url="https://keycloak.example/realms/s2gos/protocol/openid-connect/token",
    client_id="s2gos-client",
    client_secret=os.environ["S2GOS_CLIENT_SECRET"],  # omit for public clients
    username="alice",
    password=os.environ["S2GOS_PASSWORD"],
)

# Authenticated calls:
processes = client.get_processes()
```

!!! tip "Keep secrets out of source code"
    Read passwords and client secrets from environment variables (as above)
    rather than hard-coding them. Never commit credentials to version control.

### What happens under the hood

1. The client sends an OAuth2 *password grant* request to `auth_url`:

    ```
    POST <auth_url>
    Content-Type: application/x-www-form-urlencoded

    grant_type=password&username=alice&password=…&client_id=s2gos-client&client_secret=…
    ```

2. The authorization server responds with a JSON body containing an
   `access_token` and, when supported, a `refresh_token`.

3. The client retains `auth_type="login"`, the access token, and any refresh
   token in its in-memory configuration. It sends the access token on every
   request to the S2GOS service:

    ```
    Authorization: Bearer <access_token>
    ```

## Using a static token instead

If you already have an access token (for example, obtained out-of-band from
your OAuth2 server), skip the login step and provide the token directly:

```python
from s2gos_client import create_client

client = create_client(
    api_url="https://s2gos.example/",
    auth_type="token",
    token="eyJhbGciOi…",   # your access token
    use_bearer=True,        # sent as: Authorization: Bearer <token>
)
```

You can also persist a static token with the CLI so you do not have to pass it
each time:

```console
$ s2gos-client configure --api-url https://s2gos.example/ --auth-type token --token "$S2GOS_TOKEN" --use-bearer
```

This writes the settings to `~/.s2gos-client`.

## Configuration by environment variables

Any setting can be supplied via an `S2GOS_`-prefixed environment variable (or a
`.env` file in the working directory). This is convenient for CI or container
deployments:

```bash
export S2GOS_API_URL="https://s2gos.example/"
export S2GOS_AUTH_TYPE="token"
export S2GOS_TOKEN="eyJhbGciOi…"
```

```python
from s2gos_client import create_client

client = create_client()  # settings picked up from the environment
```

## Configuration file example

The configuration file `~/.s2gos-client` is YAML. A static-token setup looks
like this:

```yaml
api_url: https://s2gos.example/
auth_type: token
token: eyJhbGciOi…
use_bearer: true
```

## Token expiry and refresh

Access tokens issued by OAuth2 servers expire. For `auth_type="login"`, the
client keeps the authentication type and refresh token after the initial
password grant. On an HTTP `401 Unauthorized`, it uses the refresh token to
obtain a new access token and retries the request once.

!!! note
    Refreshed tokens are retained only by the client instance; they are not
    written back to `~/.s2gos-client`. A static `auth_type="token"` setup has
    no refresh token, so provide a new token when it expires.

## Security notes

- Never commit passwords, client secrets, or tokens to version control.
- Prefer environment variables or a protected `~/.s2gos-client` file for
  storing credentials; restrict its file permissions (`chmod 600`).
- Always use `https://` URLs for both `api_url` and `auth_url` so credentials
  and tokens are not sent in clear text.
