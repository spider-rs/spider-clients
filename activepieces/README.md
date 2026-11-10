# Spider piece for Activepieces

`@spider-cloud/piece-spider` adds [Spider](https://spider.cloud?utm_source=activepieces&utm_medium=directory&utm_campaign=activepieces-listing) to Activepieces flows and agents. It calls the Spider API at `https://api.spider.cloud`.

## Actions

| Action | Endpoint | Returns |
|---|---|---|
| Scrape page | `POST /scrape` | One page object with the content in the format you pick |
| Crawl site | `POST /crawl` | One page object per page, up to the page limit |
| Search the web | `POST /search` | Ranked results, or page objects when Fetch page content is on |
| Collect links | `POST /links` | One object per page with the links found on it |
| Custom API call | any path | The raw response, for routes the actions above don't cover |

Each content action has an Additional parameters field. It takes a JSON object with any other request parameter from the [API reference](https://spider.cloud/docs/api?utm_source=activepieces&utm_medium=directory&utm_campaign=activepieces-listing), for example `{"metadata": true}`. A field set in the form wins over the same key in that JSON.

Crawl site and Collect links default to a page limit of 10. A limit of 0 crawls every page found, capped by your credit balance.

## Connection

Create an API key at [spider.cloud/api-keys](https://spider.cloud/api-keys?utm_source=activepieces&utm_medium=directory&utm_campaign=activepieces-listing) and paste it into the connection. The piece sends it as `Authorization: Bearer <key>`.

When you save the connection, the piece calls `GET /data/credits` to check the key. That call reads your balance and spends nothing. A 401 rejects the key. A 402 means the key works but the account has no credits, so the connection still saves.

## Install on a self-hosted Activepieces

The Activepieces docs list two ways to add a piece that isn't in the official catalog. Both go through **Platform Admin → Catalogue → Pieces → Install Piece**. The server needs release 0.82.0 or later.

### From npm

Once the package is on npm, pick npm as the source and enter `@spider-cloud/piece-spider`. See [Community (public npm)](https://www.activepieces.com/docs/build-pieces/sharing-pieces/community) and [Manage pieces](https://www.activepieces.com/docs/admin-guide/guides/manage-pieces).

### From a tarball

Build the archive yourself and upload it with the Upload File source:

```bash
git clone https://github.com/spider-rs/spider-clients.git
cd spider-clients/activepieces
npm ci
npm run pack     # writes spider-cloud-piece-spider-<version>.tgz here
```

See [Install private pieces](https://www.activepieces.com/docs/admin-guide/guides/manage-pieces#install-private-pieces). The docs mark this upload as an enterprise feature.

`AP_DEV_PIECES` is not an install path. The [development setup](https://www.activepieces.com/docs/build-pieces/building-pieces/development-setup) uses it to load pieces from the `packages/pieces` folder of an Activepieces source checkout.

## Develop

```bash
npm ci
npm test          # vitest, HTTP mocked, no key or network needed
npm run build     # typecheck, then bundle to dist/
npm test          # run again after a build to also check the bundle
```

`npm run build` writes `dist/src/index.js`, one CommonJS file with the framework inlined, and a `dist/package.json` with no runtime dependencies. That is the layout Activepieces uses for its own pieces, so the server installs one artifact. The root `package.json` is private on purpose. Publish from `dist/`.

The piece builds against `@activepieces/pieces-framework` 0.32.0 and `@activepieces/pieces-common` 0.12.5 from npm.

## License

MIT
