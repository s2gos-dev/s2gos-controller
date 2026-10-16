# Configuration and authentication

The S2GOS client uses one configuration model across its Python API, CLI, and
App. Public service settings live in a YAML profile; the CLI stores login secrets
in the operating system's keyring. For the local tutorials, use a separate profile
with no authentication. For a hosted deployment, use the settings supplied by
its operator.

## Profiles and defaults

The default profile is `~/.s2gos-client`. The S2GOS factory functions
`create_client()` and `create_async_client()` select this profile and the
`S2GOS_` environment namespace. Use `config_path="profile.yaml"` in Python or
`--config profile.yaml` on CLI commands to select another profile.

Current built-in defaults in `S2GOSConfig` are:

| Setting | Default |
| --- | --- |
| `api_url` | `https://s2gos-free.wraptile.brockmann-consult.de/` |
| `auth.auth_type` | `oidc` |
| `auth.issuer_url` | `https://auth.brockmann-consult.de/realms/dte-s2gos` |
| `auth.client_id` | `cuiman` |
| `auth.scopes` | `openid` (always requested) |

By default, the S2GOS client signs you in with **OpenID Connect (OIDC)**: a
browser login to the S2GOS identity provider using the Authorization Code flow
with PKCE. You enter your password on the provider's page, never in the client.
The OAuth2 password grant is no longer used for the S2GOS service.

These are package defaults, not a guarantee of access to that deployment. Confirm
which service and account you should use with your operator. For every
authentication setting, see the Cuiman
[configuration reference](https://eo-tools.github.io/eozilla/cuiman/configuration/#authentication-settings).

For a newly created client, settings have increasing precedence: built-in defaults,
profile file, local `.env` file, process environment, supplied `config` fields,
and explicit keyword overrides. Environment variables can therefore override
settings in a selected profile. Explicit Python keyword arguments take precedence.

Authentication is a nested `auth` object. A partial override without `auth_type`
merges with the selected authentication settings. An override containing
`auth_type` replaces the previous authentication object, so supply the required
provider fields when selecting a new mechanism. See
[Replacing or merging authentication](https://eo-tools.github.io/eozilla/cuiman/configuration/#replacing-or-merging-authentication)
for examples.

## Local service: no login

From an activated environment at the repository root:

```bash
--8<-- "examples/guides/cli.sh:configure"
```

The generated profile describes this service:

```yaml
api_url: http://127.0.0.1:8008/
auth:
  auth_type: none
```

In Python, use `create_client(config_path="local-client.yaml")`, or supply both
`api_url="http://127.0.0.1:8008"` and `auth={"auth_type": "none"}` explicitly.
Changing only the API URL does not disable the S2GOS authentication defaults.

## Hosted service: configure, then log in

Run these commands in an interactive terminal:

```bash
s2gos-client configure
s2gos-client login
s2gos-client list-processes
```

`configure` prompts for the service URL and public authentication settings. Accept
the OIDC defaults unless your operator gave you other values, and check them if
you have previously used another service. For a separate profile, add
`--config s2gos-client.yaml` to each command.

`login` opens the provider's sign-in page in your browser. After you sign in,
the provider redirects the browser to a temporary callback server that the
client starts on `127.0.0.1`. The client then stores the access and refresh
tokens in the OS keyring. Use `--no-browser` to print the sign-in URL instead
of opening it.

!!! note "Browser and client must run on the same machine"

    The callback server listens on `127.0.0.1` of the machine running the
    client. If the client runs elsewhere, such as in a remote JupyterHub or over
    SSH, the redirect reaches your own computer instead and the login times
    out. For those environments, see
    [Automated runs and remote environments](#automated-runs-and-remote-environments).

Once configured, use that same profile from Python:

```python
from s2gos_client import create_client

client = create_client()
try:
    client.login()  # reuses saved tokens or opens the browser
    print(client.get_processes().model_dump_json(indent=2))
finally:
    client.close()
```

Constructing a client does not log in immediately, and requests never open a
browser. Call `login()` explicitly for an interactive login. Use `client.login(save=True)` if you also want a Python login
to save its credentials for later sessions. Plain `close()` releases connections
and does not log out or cancel server jobs.

## Supported mechanisms

| `auth.auth_type` | Purpose | Main settings inside `auth` |
| --- | --- | --- |
| `none` | Unauthenticated service | None |
| `oauth2` | OAuth2 password or client-credentials grant | `token_url`, `client_id`, `grant_type`; credentials for the selected grant |
| `oidc` | Browser login using Authorization Code with PKCE | `issuer_url`, `client_id`, optional `scopes` |
| `token` | An existing access token | `access_token`, optional `access_token_header` |
| `basic` | HTTP Basic authentication | `username`, `password` |
| `api-key` | API key in a header | `api_key`, optional `api_key_header` |
| `login` | A proprietary username/password login endpoint | `login_url`, `username`, `password` |

`oidc` is the S2GOS default. Use `oauth2` only for another service that offers an
OAuth2 token endpoint. The `login` authentication type is a different mechanism
and is not the name for OAuth2 password authentication. For an existing token,
the default is `Authorization: Bearer ...`; set `access_token_header` only when
the service expects another header. Each type is described in detail in the
Cuiman [authentication settings](https://eo-tools.github.io/eozilla/cuiman/configuration/#authentication-settings).

## Supply credentials from the environment

Nested fields use a double underscore. For example, `auth.auth_type` is set with
`S2GOS_AUTH__AUTH_TYPE`. Flat settings such as `S2GOS_TOKEN` or
`S2GOS_AUTH_TYPE` are not the current authentication interface.

OIDC needs a browser, so it has no username and password to supply through the
environment. To run without a browser login, provide an access token instead:
set `S2GOS_API_URL`, `S2GOS_AUTH__AUTH_TYPE=token`, and
`S2GOS_AUTH__ACCESS_TOKEN`. Use your shell or secret manager to provide the
values. See [Environment variables](https://eo-tools.github.io/eozilla/cuiman/configuration/#environment-variables) for the full
naming scheme.

Do not put passwords, access tokens, or client secrets in example request files.

## Automated runs and remote environments

For unattended jobs on your own machine, sign in once with `s2gos-client login`.
Later Python sessions and CLI commands using the same profile reuse the saved
tokens from the OS keyring and renew them without opening a browser. Use
`client.login(interactive=False)` to fail early if authentication cannot proceed.
The CLI requires a profile even when environment variables supply credentials.

Where no browser can complete the login, for example in a remote JupyterHub,
the deployment must supply an access token through the environment as described
above. An injected token is not renewed automatically; when the API rejects it,
fresh credentials are needed. See
[Remote notebooks](https://eo-tools.github.io/eozilla/cuiman/configuration/#remote-notebooks) in the Cuiman documentation.

OIDC sessions renew their access tokens using the refresh token. If a saved
login no longer works, use `s2gos-client login --force` with the appropriate
profile. Use `s2gos-client logout` to remove its stored credentials when you
intend to sign out. The OS keyring has no plaintext-file fallback; see
[Credential storage](https://eo-tools.github.io/eozilla/cuiman/configuration/#credential-storage).

For missing credentials or keyring errors, check that you are using the same
profile, service URL, and account as during login. For authorization failures,
confirm your account has permission for that service. Data-storage credentials
are separate; see [Working with results](guide/results.md#access-data-from-a-hosted-service).
