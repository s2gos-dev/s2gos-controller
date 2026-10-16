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
| `auth.auth_type` | `oauth2` |
| `auth.token_url` | `https://kc.dev.brockmann-consult.de/realms/dte-s2gos/protocol/openid-connect/token` |
| `auth.client_id` | `cuiman` |
| `auth.grant_type` | `password` |

These are package defaults, not a guarantee of access to that deployment. Confirm
which service and account you should use with your operator.

For a newly created client, settings have increasing precedence: built-in defaults,
profile file, local `.env` file, process environment, supplied `config` fields,
and explicit keyword overrides. Environment variables can therefore override
settings in a selected profile. Explicit Python keyword arguments take precedence.

Authentication is a nested `auth` object. A partial override without `auth_type`
merges with the selected authentication settings. An override containing
`auth_type` replaces the previous authentication object, so supply the required
provider fields when selecting a new mechanism.

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

`configure` prompts for the service URL and public authentication settings. Check
the displayed defaults, especially if you have previously used another service.
`login` obtains credentials and stores them in the OS keyring. For a separate
profile, add `--config s2gos-client.yaml` to each command.

Once configured, use that same profile from Python:

```python
from s2gos_client import create_client

client = create_client()
try:
    client.login()  # reuses credentials or prompts when needed
    print(client.get_processes().model_dump_json(indent=2))
finally:
    client.close()
```

Constructing a client does not log in immediately. Requests can acquire tokens
from supplied credentials without prompting; call `login()` explicitly for an
interactive login. Use `client.login(save=True)` if you also want a Python login
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

Use `oauth2` for an OAuth2 token endpoint. The `login` authentication type is a
different mechanism and is not the name for OAuth2 password authentication.
For an existing token, the default is `Authorization: Bearer ...`; set
`access_token_header` only when the service expects another header.

## Supply credentials from the environment

Nested fields use a double underscore. For example, set
`S2GOS_AUTH__USERNAME` and `S2GOS_AUTH__PASSWORD` in your environment to supply
credentials for the default OAuth2 configuration. Keep the provider fields
unchanged by omitting `S2GOS_AUTH__AUTH_TYPE` when you only need to add credentials.

For static-token access, set `S2GOS_API_URL`,
`S2GOS_AUTH__AUTH_TYPE=token`, and `S2GOS_AUTH__ACCESS_TOKEN`.
Use your shell or secret manager to provide the values. Flat settings such as
`S2GOS_TOKEN` or `S2GOS_AUTH_TYPE` are not the current authentication interface.

You can also pass credentials explicitly from environment variables in Python:

```python
import os
from s2gos_client import create_client

client = create_client(
    auth={
        "username": os.environ["S2GOS_AUTH__USERNAME"],
        "password": os.environ["S2GOS_AUTH__PASSWORD"],
    }
)
try:
    client.login(interactive=False)
    print(client.get_processes().model_dump_json(indent=2))
finally:
    client.close()
```

This partial `auth` override assumes the selected profile uses OAuth2 password
authentication. For another provider, configure its token URL and client ID first.
Do not put passwords, access tokens, or client secrets in example request files.

## Automated runs and token lifetime

In unattended Python jobs, supply credentials through the environment and use
`client.login(interactive=False)` to fail early if authentication cannot proceed.
The CLI requires a profile even when environment variables supply credentials.
Create that profile before running your job. `s2gos-client login --no-input`
uses supplied credentials without prompts and saves them to the OS keyring, so
it also requires a working keyring. Ordinary API calls can use credentials
provided at runtime without saving them.

OAuth2/OIDC sessions can renew tokens when the provider supplies the necessary
refresh information. A static token has no automatic refresh flow; replace it
when it expires. If a saved login no longer works, use
`s2gos-client login --force` with the appropriate profile. Use
`s2gos-client logout` to remove its stored credentials when you intend to sign out.

For missing credentials or keyring errors, check that you are using the same
profile, service URL, and account as during login. For authorization failures,
confirm your account has permission for that service. Data-storage credentials
are separate; see [Working with results](guide/results.md#access-data-from-a-hosted-service).
