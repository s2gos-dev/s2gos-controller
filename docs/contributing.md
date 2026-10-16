# Contributing to the project

Contributions are welcome through the
[issue tracker](https://github.com/s2gos-dev/s2gos-controller/issues) and
[pull requests](https://github.com/s2gos-dev/s2gos-controller/pulls).
Read the [contribution guide](https://github.com/s2gos-dev/s2gos-controller/blob/main/CONTRIBUTING.md)
and [code of conduct](https://github.com/s2gos-dev/s2gos-controller/blob/main/CODE_OF_CONDUCT.md).
Document user-visible changes in
[CHANGES.md](https://github.com/s2gos-dev/s2gos-controller/blob/main/CHANGES.md).

## Development setup

Follow [Installation](installation.md#using-github), then work from the repository
root inside `pixi shell`. See [Getting started](guide/index.md) for the local
server and client workflow. Use `s2gos-server dev -- wraptile.services.local.testing:service`
when you need the server to reload after code changes.

```bash
pixi run format
pixi run checks
pixi run tests
pixi run coverage
```

Before a release, update the version in the root `pyproject.toml` and synchronize
package versions with `pixi run sync-versions`.

## Maintain the user guide

The user guide is maintained as Markdown in `docs/guide/`, with shared
configuration and authentication documentation in `docs/auth.md`. Original
notebooks remain under `notebooks/` for exploration. They are not copied or
rendered during documentation builds. Old generated files under `docs/notebooks/`
are excluded from the site, including any local configuration files left there.

Reusable Python, shell, and JSON examples live in `examples/guides/`. Include
code using `pymdownx.snippets` rather than maintaining a second copy in Markdown.
Named sections use matching `# --8<-- [start:name]` and
`# --8<-- [end:name]` comments. The build fails if a snippet path is missing.
Keep imports, variable definitions, and cleanup clear when splitting examples
across multiple blocks. If a snippet needs an earlier step, say so in the prose.

Examples should use the local test service, retain server-assigned job IDs, and
close clients and datasets. Imports must not connect, submit jobs, or start an
App. Explain how to adapt the workflow to hosted S2GOS without publishing
credentials or assuming a particular scientific process is installed.

The client test suite checks the example workflows, including failure handling,
App cleanup, and opening an actual local Zarr result. Example code participates
in formatting, linting, type checking, and client coverage. When you change a
snippet, validate the rendered walkthrough as well as its Python module.

```bash
pixi run gen-cli-docs
pixi run doc-build
pixi run doc-serve
```

The CLI reference pages are generated; update them with `gen-cli-docs` after
changing CLI behavior. `doc-build` uses strict mode, also in CI. Preview changed
pages and check headings, code blocks, links, and navigation before submitting.

If adding a screenshot, capture the current App against the local test service,
keep credentials and private job data out of the image, and record the process,
inputs, App version or revision, and capture steps alongside the asset so it can
be reproduced.

## License

The project is available under the
[Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0.html).
