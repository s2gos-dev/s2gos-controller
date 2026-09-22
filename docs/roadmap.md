# S2GOS Controller Roadmap

Given here is the S2GOS controller development plan including the features and issues 
that are worked on and will be addressed next.

_Updated on 2026-09-22_

Detailed issue descriptions can be found in the related issue trackers:

- [Eozilla](https://github.com/eo-tools/eozilla/issues)
- [S2GOS Controller](https://github.com/s2gos-dev/s2gos-controller/issues)

## Ongoing

Server / DestinE Onboarding: 

- Onboarding free tier service (demo service is already available).
- Deploying and testing different processes based on different generator 
  and simulator configurations on OVH Airflow.
- Allow for per-user outputs on OVH object storage.

Client: 

- hook into DestinE JupyterLab authentication flow to reuse its access tokens 
  when making server calls.
- Ease accessing processor outputs (implementing new client job result openers)

## Next

### Client General

- Allow for passing user files as inputs.
- Allow for branding the app for the `display="browser"` mode.

### Authorisation

- Define user roles & scopes Keycloak and use them in the server 
