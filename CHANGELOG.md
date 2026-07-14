# Changelog

All notable changes to the Spider client libraries are documented here. Each
language client is versioned and released independently (different package
ecosystems) — see [Releasing](#releasing) for how versions map to git tags.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## 2026-07-14

### Added

- **Unlimited plan routes.** New methods for the flat-rate Unlimited plan —
  `/unlimited/scrape`, `/unlimited/crawl`, `/unlimited/links` — billed by
  purchased concurrency seats rather than per-request credits. Requires an
  active Unlimited subscription
  ([pricing](https://spider.cloud/pricing?plan=unlimited),
  [docs](https://spider.cloud/docs/api/unlimited)). Python
  (`unlimited_scrape`/`unlimited_crawl`/`unlimited_links`, sync and async),
  JavaScript (`unlimitedScrape`/`unlimitedCrawl`/`unlimitedLinks`), Go
  (`UnlimitedScrapeURL`/`UnlimitedCrawlURL`+`Stream`/`UnlimitedLinks`, plus
  typed `UnlimitedPlanRequired`/`UnlimitedConcurrencyLimitReached` errors and
  a `Concurrency` field tracking the `X-Concurrency-*` headers), and Rust
  (`unlimited_scrape`/`unlimited_crawl`/`unlimited_links`). Requests beyond
  the purchased seats get an immediate `429` with `Retry-After` (no
  queueing); AI/LLM extraction params are rejected with `400`.
- **AI routes for Rust and async Python.** The Rust client gains
  `ai_crawl`/`ai_scrape`/`ai_search`/`ai_browser`/`ai_links`, and Python's
  `AsyncSpider` reaches AI parity with the sync client. AI routes require an
  active AI Studio subscription, billed separately:
  https://spider.cloud/ai/pricing

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

### Client versions

| Client     | Package                                       | Version  | Release tag    |
| ---------- | --------------------------------------------- | -------- | -------------- |
| JavaScript | `@spider-cloud/spider-client` (npm)           | `0.2.3`  | `js-v0.2.3`    |
| Python     | `spider_client` (PyPI)                        | `0.1.91` | `py-v0.1.91`   |
| Rust       | `spider-client` (crates.io)                   | `0.1.90` | `rust-v0.1.90` |
| CLI        | `spider-cloud-cli` (crates.io)                | `0.1.90` | `cli-v0.1.90`  |
| Go         | `github.com/spider-rs/spider-clients/go`      | `0.1.91` | `go/v0.1.91`   |

> Note: `js-v0.2.1`/`js-v0.2.2`, `rust-v0.1.88`/`rust-v0.1.89`, and
> `cli-v0.1.88`/`cli-v0.1.89` were tagged but never reached their registries —
> the npm publish lacked an `NPM_TOKEN` secret and the crates.io token had been
> revoked (pre-2020 token format). This release supersedes them; the CLI has no
> code changes since `0.1.89`, it is a registry catch-up release.

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
