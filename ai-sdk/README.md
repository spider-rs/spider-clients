# @spider-cloud/ai-sdk

Spider tools for the [Vercel AI SDK](https://ai-sdk.dev). They give a model four tools that call the [Spider API](https://spider.cloud/?utm_source=vercel-ai-sdk&utm_medium=directory&utm_campaign=vercel-ai-sdk-listing):

| Tool | Route | What the model gets |
|---|---|---|
| `scrape` | `POST /scrape` | One page as markdown, text or raw HTML |
| `crawl` | `POST /crawl` | The content of each page found from a start URL |
| `search` | `POST /search` | Ranked results with title, description and URL, or each result's page content |
| `links` | `POST /links` | The URLs linked from a page or a short crawl |

The package has no runtime dependencies. It calls the API with `fetch` and declares `ai` and `zod` as peer dependencies.

## Install

```bash
npm install @spider-cloud/ai-sdk ai zod
```

## API key

Create a key at [spider.cloud/api-keys](https://spider.cloud/api-keys?utm_source=vercel-ai-sdk&utm_medium=directory&utm_campaign=vercel-ai-sdk-listing) and set it in the environment:

```bash
export SPIDER_API_KEY=your-key
```

`scrape` also works without a key, on a rate limited keyless tier. `crawl`, `search` and `links` need a key and throw before sending a request when none is set.

## Use

```ts
import { generateText, isStepCount } from "ai";
import { spiderTools } from "@spider-cloud/ai-sdk";

const { text } = await generateText({
  model: "openai/gpt-5-mini",
  prompt: "Find the latest Rust release notes and summarize the main changes.",
  tools: spiderTools(),
  stopWhen: isStepCount(5),
});

console.log(text);
```

Pick single tools if the model only needs some of them:

```ts
import { spiderScrape, spiderSearch } from "@spider-cloud/ai-sdk";

const tools = {
  search: spiderSearch({ maxResults: 5 }),
  scrape: spiderScrape({ maxContentChars: 20_000 }),
};
```

## Options

Every tool factory takes the same base options:

| Option | Default | Meaning |
|---|---|---|
| `apiKey` | `process.env.SPIDER_API_KEY` | Spider API key |
| `baseUrl` | `https://api.spider.cloud` | API base URL |
| `fetch` | global `fetch` | Custom fetch, for tests or proxies |
| `headers` | none | Extra headers on every request |
| `maxContentChars` | no limit | Cut each page's content to this length before it reaches the model |
| `params` | none | Spider request fields sent on every call, such as `{ request: "browser", readability: true }`. The model's arguments override them. |

`spiderCrawl` and `spiderLinks` also take `maxPages` (default 20), the largest `limit` the model may ask for. `spiderSearch` takes `maxResults` (default 10). The schema rejects larger values before any request goes out, so a model cannot start a large crawl by itself.

The full list of request fields is in the [OpenAPI spec](https://spider.cloud/openapi.yaml?utm_source=vercel-ai-sdk&utm_medium=directory&utm_campaign=vercel-ai-sdk-listing).

## Errors

A non 2xx answer throws `SpiderApiError` with `status`, `body` and, on 429, `retryAfter` in seconds from the `Retry-After` header. The AI SDK passes the error message to the model as a tool error.

## Compatibility

The source builds against `ai` 5, 6 and 7. The tests run against `ai` 7.

## Develop

```bash
npm install
npm run typecheck
npm test
npm run build
```

The tests mock `fetch` and never call the network.

## License

MIT
