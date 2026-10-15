# Authentication

The S2GOS client authenticates requests to the S2GOS service (an
OGC API - Processes server) using standard HTTP mechanisms. There is **no
provider-specific code**: the client speaks generic OAuth2 / OIDC and HTTP
auth, so it works with any compliant authorization server: Keycloak, Auth0,
Azure AD, or a plain token issuer.

This page explains how to configure the client, with a focus on connecting it
to an **OpenID Connect / OAuth2 authorization server**.

## Supported authentication types

Authentication settings live in a nested `auth` section of the client
configuration. Its `auth_type` selects how the client authenticates:

| `auth_type` | How it works | Required settings |
|-------------|--------------|-------------------|
| `none`      | No authentication. | — |
| `oidc`      | OpenID Connect *Authorization Code + PKCE*: sign in through the browser, then send the access token as a bearer and refresh it automatically. **This is the default.** | `issuer_url`, `client_id` |
| `oauth2`    | OAuth2 *password* or *client-credentials* grant against a token endpoint; tokens are refreshed automatically. | `token_url`, `client_id`, plus `username`/`password` (password grant) or `client_secret` (client credentials) |
| `token`     | Send a pre-obtained static access token. | `access_token` |
| `login`     | Exchange username/password at a *proprietary* (non-OAuth2) login endpoint for an access token. | `login_url`, `username`, `password` |
| `api-key`   | Send an API key in a custom header. | `api_key` |
| `basic`     | HTTP Basic Auth. | `username`, `password` |

For the hosted S2GOS service you normally use **`oidc`** (interactive sign-in)
or **`token`** (if you already hold an access token, e.g. inside JupyterHub).

## Configuration settings

| Setting | Description |
|---------|-------------|
| `api_url` | URL of the S2GOS service (OGC API - Processes). Top-level setting. |
| `auth.auth_type` | One of the types above. |
| `auth.issuer_url` | OIDC issuer URL (`oidc`), e.g. a Keycloak realm URL. Endpoints are discovered from `<issuer_url>/.well-known/openid-configuration`. |
| `auth.scopes` | Extra OIDC scopes (`oidc`); `openid` is always included. |
| `auth.token_url` | OAuth2 **token endpoint** (`oauth2`). |
| `auth.grant_type` | `password` (default) or `client_credentials` (`oauth2`). |
| `auth.client_id` / `auth.client_secret` | OAuth2/OIDC client. `client_secret` is only needed for *confidential* clients. |
| `auth.username` / `auth.password` | User credentials (`oauth2` password grant, `login`, `basic`). |
| `auth.access_token` | Static access token (`token`, or obtained by `login`). |
| `auth.access_token_header` | Send the raw token in this header instead of `Authorization: Bearer <token>` (`token`, `login`). |
| `auth.oauth_token` | The OAuth2/OIDC token set (access + refresh token), managed by the client. |
| `auth.api_key` / `auth.api_key_header` | API key and its header (default `X-API-Key`) for `api-key`. |

### Where settings come from

Settings are merged from several sources, in increasing order of precedence:

1. Built-in defaults.
2. The configuration file `~/.s2gos-client` (YAML).
3. A local `.env` file, then environment variables prefixed with `S2GOS_`.
   Nested `auth` settings use a double underscore, e.g. `S2GOS_AUTH__AUTH_TYPE`.
4. Values passed directly in Python (`create_client(**settings)`).

So a value passed in code overrides an environment variable, which overrides
the config file. Passing an `auth` mapping that contains `auth_type` replaces
the whole `auth` section; one without `auth_type` is merged into it.

### Where secrets are stored

Secrets (passwords, client secrets, access/refresh tokens, API keys) are **not**
written to `~/.s2gos-client`. `s2gos-client login` stores them in the operating
system **keyring**, and the client reads them from there when the configuration
does not supply them. `s2gos-client logout` removes them again.

### Default configuration

Out of the box, the client is preconfigured for the hosted S2GOS service and
its Keycloak realm, so a plain `create_client()` targets that deployment. The
built-in defaults are:

| Setting | Default |
|---------|---------|
| `api_url` | `https://s2gos-free.wraptile.brockmann-consult.de/` |
| `auth.auth_type` | `oidc` (Authorization Code + PKCE) |
| `auth.issuer_url` | `https://auth.brockmann-consult.de/realms/dte-s2gos` |
| `auth.client_id` | `cuiman` |
| `auth.scopes` | `openid` |

Because `auth_type` defaults to `oidc`, signing in opens a browser login at
the Keycloak realm (which can hand off to DestinE IAM); no username or
password is handled by the client. Override any default by passing it to
`create_client`, setting the matching `S2GOS_*` environment variable, or storing
it in `~/.s2gos-client` — for example, point `api_url` / `auth.issuer_url` at a
different deployment, or use `auth_type="token"` inside JupyterHub.

## Signing in with OIDC (default)

From the command line:

```console
$ s2gos-client login
```

This opens a browser at the authorization server; after you sign in, the
token is saved in the keyring and reused by both the CLI and Python. Use
`--no-browser` to print the authorization URL instead (e.g. over SSH), and
`--force` to discard the stored token and sign in again.

A configuration file for the default deployment looks like this:

```yaml
api_url: https://s2gos-free.wraptile.brockmann-consult.de/
auth:
  auth_type: oidc
  issuer_url: https://auth.brockmann-consult.de/realms/dte-s2gos
  client_id: cuiman
```

You can write it interactively with `s2gos-client configure`, or
non-interactively:

```console
$ s2gos-client configure --api-url https://s2gos-free.wraptile.brockmann-consult.de/ \
    --auth-type oidc \
    --issuer-url https://auth.brockmann-consult.de/realms/dte-s2gos \
    --client-id cuiman
```

In Python, `create_client()` picks up the stored token; call
`client.login()` (or `client.login(force=True)`) to sign in from a notebook.
Pass `save=True` to also store the new token in the keyring.

!!! note "OIDC needs a browser on the same machine"
    The Authorization Code flow redirects back to a loopback address on the
    machine running the client. Where that is not possible (e.g. a remote
    JupyterHub server), use a static `token` instead.

## Using the OAuth2 password grant

For scripts and CI you can exchange a username and password for a token at the
token endpoint. For a **Keycloak** realm it looks like:

```
https://<keycloak-host>/realms/<realm>/protocol/openid-connect/token
```

```python
import os
from s2gos_client import create_client

client = create_client(
    api_url="https://s2gos.example/",
    auth={
        "auth_type": "oauth2",
        "token_url": "https://keycloak.example/realms/s2gos/protocol/openid-connect/token",
        "client_id": "s2gos-client",
        "client_secret": os.environ.get("S2GOS_CLIENT_SECRET"),  # confidential clients only
        "username": "alice",
        "password": os.environ["S2GOS_PASSWORD"],
    },
)

processes = client.get_processes()
```

!!! warning "The client must allow direct access grants"
    The password grant only works if the authorization server permits it for
    the client (in Keycloak: *Direct access grants* enabled). The default
    `cuiman` client of the hosted S2GOS realm does **not** allow it and
    rejects the request with `unauthorized_client`; use `oidc` there.

Under the hood the client sends

```
POST <token_url>
Content-Type: application/x-www-form-urlencoded

grant_type=password&username=alice&password=…&client_id=s2gos-client
```

and sends the returned access token as `Authorization: Bearer <access_token>`
on every request, refreshing it with the refresh token before it expires.

!!! tip "Keep secrets out of source code"
    Read passwords and client secrets from environment variables (as above)
    rather than hard-coding them. Never commit credentials to version control.

## Using a static token instead

If you already have an access token (for example, obtained out-of-band from
your authorization server, or injected by JupyterHub), provide it directly:

```python
from s2gos_client import create_client

client = create_client(
    auth={"auth_type": "token", "access_token": "eyJhbGciOi…"},
)
```

The token is sent as `Authorization: Bearer <token>`, or in
`access_token_header` if you set one. A static token is not refreshed;
provide a new one when it expires.

## Configuration by environment variables

Any setting can be supplied via an `S2GOS_`-prefixed environment variable (or a
`.env` file in the working directory), using `__` for nested `auth` settings.
This is convenient for CI, containers, and JupyterHub:

```bash
export S2GOS_API_URL="https://s2gos.example/"
export S2GOS_AUTH__AUTH_TYPE="token"
export S2GOS_AUTH__ACCESS_TOKEN="eyJhbGciOi…"
```

```python
from s2gos_client import create_client

client = create_client()  # settings picked up from the environment
```

## Token expiry and refresh

For `oidc` and `oauth2`, the client refreshes the access token with the
refresh token before it expires.
If the refresh token itself has expired (e.g. after a long idle period), sign
in again with `s2gos-client login --force` or `client.login(force=True)`.

## Security notes

- Never commit passwords, client secrets, or tokens to version control.
- Prefer `oidc` or environment variables over storing credentials in code;
  secrets obtained via `s2gos-client login` are kept in the OS keyring.
- Always use `https://` URLs for `api_url`, `issuer_url`, and `token_url` so
  credentials and tokens are not sent in clear text.
