# Changelog

All notable changes to the Spider client libraries are documented here. Each
language client is versioned and released independently (different package
ecosystems) — see [Releasing](#releasing) for how versions map to git tags.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed

- **Python unit tests mock the right boundary.** The sync client tests patched
  `requests.post`/`requests.get`, but the client routes every call through a
  persistent `requests.Session` (`self._session`), so the patches never
  intercepted and the "unit" tests made real 401'd API calls in CI. They now
  patch `Spider._post_request`/`_get_request`, unblocking the PyPI release.
- **Go module is now consumable.** `go/go.mod` pinned
  `github.com/spider-rs/spider-browser/go` to the published `v0.3.0` and dropped
  the local `replace` directive (a dev-only path that broke `go build` for every
  external consumer and the release workflow). Go bumped `0.1.89 -> 0.1.90`
  (`go/v0.1.90`); `go/v0.1.89` carries the coordinate-localization fields but an
  unbuildable `go.mod`, so use `v0.1.90`.

## 2026-06-26

### Added

- **Coordinate localization for search.** The search request now accepts
  `latitude` and `longitude` for exact-coordinate localization, plus an optional
  `radius` (bias radius in meters; `-1` = unset). Applies to the Go, Python,
  Rust, JavaScript, and CLI clients. The CLI exposes `--latitude`,
  `--longitude`, and `--radius` on the `search` command.

### Client versions

| Client     | Package                                       | Version  | Release tag    |
| ---------- | --------------------------------------------- | -------- | -------------- |
| JavaScript | `@spider-cloud/spider-client` (npm)           | `0.2.2`  | `js-v0.2.2`    |
| Python     | `spider_client` (PyPI)                        | `0.1.90` | `py-v0.1.90`   |
| Rust       | `spider-client` (crates.io)                   | `0.1.89` | `rust-v0.1.89` |
| CLI        | `spider-cloud-cli` (crates.io)                | `0.1.89` | `cli-v0.1.89`  |
| Go         | `github.com/spider-rs/spider-clients/go`      | `0.1.89` | `go/v0.1.89`   |

## 2026-06-21

### Added

- **`browser` request type.** The `request` parameter now accepts `"browser"`
  to render with Spider's custom browser. The previous `"chrome"` value is kept
  as a deprecated, still-accepted alias, so existing integrations keep working
  unchanged. Applies to the Go, Python, Rust, and JavaScript clients.
- **Automated releases from CI.** Tag-triggered GitHub Actions workflows now
  publish every client (npm, PyPI, crates.io, Go module). See
  [Releasing](#releasing).

### Client versions

| Client     | Package                                       | Version  | Release tag    |
| ---------- | --------------------------------------------- | -------- | -------------- |
| JavaScript | `@spider-cloud/spider-client` (npm)           | `0.2.1`  | `js-v0.2.1`    |
| Python     | `spider_client` (PyPI)                        | `0.1.89` | `py-v0.1.89`   |
| Rust       | `spider-client` (crates.io)                   | `0.1.88` | `rust-v0.1.88` |
| CLI        | `spider-cloud-cli` (crates.io)                | `0.1.88` | `cli-v0.1.88`  |
| Go         | `github.com/spider-rs/spider-clients/go`      | `0.1.88` | `go/v0.1.88`   |

## Releasing

Releases are automated via GitHub Actions. To cut a release: bump the version in
the client's manifest, commit to `main`, then push a client-prefixed tag. The
matching workflow builds and publishes the package.

| Client     | Bump file                  | Tag to push                | Publishes to        |
| ---------- | -------------------------- | -------------------------- | ------------------- |
| JavaScript | `javascript/package.json`* | `js-vX.Y.Z`                | npm                 |
| Python     | `python/setup.py`          | `py-vX.Y.Z` (or `vX.Y.Z`)  | PyPI                |
| Rust       | `rust/Cargo.toml`          | `rust-vX.Y.Z`              | crates.io           |
| CLI        | `cli/Cargo.toml`           | `cli-vX.Y.Z`               | crates.io           |
| Go         | `go/config.go` (`Version`) | `go/vX.Y.Z`                | Go module proxy     |

\* Also bump `javascript/package-lock.json` (keep it in sync, or run `npm i
--package-lock-only`). Each release workflow asserts that the tag version
matches the manifest version and fails fast on a mismatch.

> **Order matters for crates.io:** publish `rust-v*` before `cli-v*` — the CLI
> depends on the published `spider-client` crate.

Example — releasing the JavaScript client `0.2.1`:

```sh
# package.json/package-lock.json already at 0.2.1, committed to main
git tag js-v0.2.1
git push origin js-v0.2.1   # → release-js.yml publishes to npm
```

### Required repository secrets

| Secret                  | Used by              | Notes                              |
| ----------------------- | -------------------- | ---------------------------------- |
| `NPM_TOKEN`             | `release-js.yml`     | npm automation token (publish)     |
| `CARGO_REGISTRY_TOKEN`  | `release-rust.yml`, `release-cli.yml` | crates.io API token |
| `PYPI_API_TOKEN`        | `release-python.yml` | PyPI API token (already configured) |
| `GITHUB_TOKEN`          | `release-go.yml`     | provided automatically by Actions  |

The manual fallback `deploy.sh` (publish all from a workstation) remains
available.
