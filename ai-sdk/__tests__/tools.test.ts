import { afterEach, beforeEach, describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { generateText, isStepCount } from "ai";
import { MockLanguageModelV4 } from "ai/test";
import {
  SpiderApiError,
  VERSION,
  spiderCrawl,
  spiderLinks,
  spiderScrape,
  spiderSearch,
  spiderTools,
} from "../src/index.js";

type Call = { url: string; init: RequestInit; body: Record<string, unknown> };

function mockFetch(
  respond: (call: Call) => Response | Promise<Response> = () => json([]),
): { fetch: typeof globalThis.fetch; calls: Call[] } {
  const calls: Call[] = [];
  const fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    const call: Call = {
      url: String(input),
      init: init ?? {},
      body: init?.body ? JSON.parse(String(init.body)) : {},
    };
    calls.push(call);
    return respond(call);
  }) as typeof globalThis.fetch;
  return { fetch, calls };
}

function json(data: unknown, status = 200, headers: Record<string, string> = {}): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json", ...headers },
  });
}

const execOpts = { toolCallId: "call-1", messages: [] } as never;

function headersOf(call: Call): Record<string, string> {
  return call.init.headers as Record<string, string>;
}

let savedKey: string | undefined;
beforeEach(() => {
  savedKey = process.env.SPIDER_API_KEY;
  delete process.env.SPIDER_API_KEY;
});
afterEach(() => {
  if (savedKey === undefined) delete process.env.SPIDER_API_KEY;
  else process.env.SPIDER_API_KEY = savedKey;
});

describe("spiderScrape", () => {
  it("posts to /scrape with markdown by default and no key", async () => {
    const m = mockFetch(() =>
      json([{ url: "https://example.com", content: "# Example", status: 200, error: null, costs: {} }]),
    );
    const t = spiderScrape({ fetch: m.fetch });
    const out = await t.execute!({ url: "https://example.com" }, execOpts);

    assert.equal(m.calls.length, 1);
    assert.equal(m.calls[0].url, "https://api.spider.cloud/scrape");
    assert.equal(m.calls[0].init.method, "POST");
    assert.deepEqual(m.calls[0].body, { return_format: "markdown", url: "https://example.com" });
    assert.equal(headersOf(m.calls[0]).Authorization, undefined);
    assert.equal(headersOf(m.calls[0])["User-Agent"], `spider-ai-sdk/${VERSION}`);
    assert.deepEqual(out, { url: "https://example.com", status: 200, content: "# Example" });
  });

  it("sends the key from SPIDER_API_KEY as a bearer token", async () => {
    process.env.SPIDER_API_KEY = "test-key";
    const m = mockFetch(() => json([{ url: "https://example.com", content: "x", status: 200 }]));
    await spiderScrape({ fetch: m.fetch }).execute!({ url: "https://example.com" }, execOpts);
    assert.equal(headersOf(m.calls[0]).Authorization, "Bearer test-key");
  });

  it("merges params under the model's input and honors baseUrl", async () => {
    const m = mockFetch(() => json([{ url: "https://example.com", content: "x", status: 200 }]));
    const t = spiderScrape({
      fetch: m.fetch,
      apiKey: "k",
      baseUrl: "https://proxy.test/",
      params: { return_format: "text", stealth: true },
    });
    await t.execute!({ url: "https://example.com", return_format: "raw" }, execOpts);
    assert.equal(m.calls[0].url, "https://proxy.test/scrape");
    assert.deepEqual(m.calls[0].body, {
      return_format: "raw",
      stealth: true,
      url: "https://example.com",
    });
  });

  it("cuts content to maxContentChars", async () => {
    const m = mockFetch(() => json([{ url: "https://example.com", content: "abcdefghij", status: 200 }]));
    const out = (await spiderScrape({ fetch: m.fetch, maxContentChars: 4 }).execute!(
      { url: "https://example.com" },
      execOpts,
    )) as { content: string };
    assert.equal(out.content, "abcd");
  });
});

describe("spiderCrawl", () => {
  it("refuses to call the API without a key", async () => {
    const m = mockFetch();
    await assert.rejects(
      async () => spiderCrawl({ fetch: m.fetch }).execute!({ url: "https://example.com" }, execOpts),
      /needs an API key/,
    );
    assert.equal(m.calls.length, 0);
  });

  it("defaults to five pages and returns one entry per page", async () => {
    const m = mockFetch(() =>
      json([
        { url: "https://example.com", content: "a", status: 200, error: null },
        { url: "https://example.com/about", content: null, status: 404, error: "not found" },
      ]),
    );
    const out = await spiderCrawl({ fetch: m.fetch, apiKey: "k" }).execute!(
      { url: "https://example.com" },
      execOpts,
    );
    assert.equal(m.calls[0].url, "https://api.spider.cloud/crawl");
    assert.deepEqual(m.calls[0].body, { return_format: "markdown", limit: 5, url: "https://example.com" });
    assert.deepEqual(out, [
      { url: "https://example.com", status: 200, content: "a" },
      { url: "https://example.com/about", status: 404, error: "not found" },
    ]);
  });
});

describe("spiderSearch", () => {
  it("sends the query as search and returns ranked results", async () => {
    const m = mockFetch(() =>
      json({
        content: [
          { title: "spider-rs/spider", description: "A web crawler.", url: "https://github.com/spider-rs/spider" },
        ],
      }),
    );
    const out = await spiderSearch({ fetch: m.fetch, apiKey: "k" }).execute!(
      { query: "rust web crawler", search_limit: 3 },
      execOpts,
    );
    assert.equal(m.calls[0].url, "https://api.spider.cloud/search");
    assert.deepEqual(m.calls[0].body, { search_limit: 3, search: "rust web crawler" });
    assert.deepEqual(out, {
      results: [
        { title: "spider-rs/spider", description: "A web crawler.", url: "https://github.com/spider-rs/spider" },
      ],
    });
  });

  it("returns pages when fetch_page_content is set", async () => {
    const m = mockFetch(() => json([{ url: "https://a.test", content: "# A", status: 200 }]));
    const out = await spiderSearch({ fetch: m.fetch, apiKey: "k" }).execute!(
      { query: "a", fetch_page_content: true },
      execOpts,
    );
    assert.deepEqual(m.calls[0].body, {
      return_format: "markdown",
      search_limit: 5,
      fetch_page_content: true,
      search: "a",
    });
    assert.deepEqual(out, { pages: [{ url: "https://a.test", status: 200, content: "# A" }] });
  });
});

describe("spiderLinks", () => {
  it("returns the links of each page", async () => {
    const m = mockFetch(() =>
      json([{ url: "https://example.com", status: 200, error: null, links: ["https://example.com/about"] }]),
    );
    const out = await spiderLinks({ fetch: m.fetch, apiKey: "k" }).execute!(
      { url: "https://example.com" },
      execOpts,
    );
    assert.equal(m.calls[0].url, "https://api.spider.cloud/links");
    assert.deepEqual(m.calls[0].body, { limit: 1, url: "https://example.com" });
    assert.deepEqual(out, [{ url: "https://example.com", status: 200, links: ["https://example.com/about"] }]);
  });
});

describe("errors", () => {
  it("throws SpiderApiError with Retry-After on 429", async () => {
    const m = mockFetch(() => json({ error: "slow down" }, 429, { "Retry-After": "7" }));
    await assert.rejects(
      async () => spiderScrape({ fetch: m.fetch }).execute!({ url: "https://example.com" }, execOpts),
      (err: unknown) => {
        assert.ok(err instanceof SpiderApiError);
        assert.equal(err.status, 429);
        assert.equal(err.retryAfter, 7);
        assert.match(err.message, /Retry after 7s/);
        return true;
      },
    );
  });

  it("points to the key page on 402", async () => {
    const m = mockFetch(() => json({ error: "Your credit balance is empty.", code: "credits_required" }, 402));
    await assert.rejects(
      async () => spiderCrawl({ fetch: m.fetch, apiKey: "k" }).execute!({ url: "https://example.com" }, execOpts),
      /402.*spider\.cloud\/api-keys/s,
    );
  });
});

describe("with generateText", () => {
  it("runs a tool call from the model and feeds the result back", async () => {
    const m = mockFetch(() => json([{ url: "https://example.com", content: "# Example Domain", status: 200 }]));
    const usage = {
      inputTokens: { total: 1, noCache: 1, cacheRead: 0, cacheWrite: 0 },
      outputTokens: { total: 1, text: 1, reasoning: 0 },
    };
    const model = new MockLanguageModelV4({
      doGenerate: [
        {
          content: [
            {
              type: "tool-call",
              toolCallId: "c1",
              toolName: "scrape",
              input: JSON.stringify({ url: "https://example.com" }),
            },
          ],
          finishReason: { unified: "tool-calls", raw: undefined },
          usage,
          warnings: [],
        },
        {
          content: [{ type: "text", text: "It is an example page." }],
          finishReason: { unified: "stop", raw: undefined },
          usage,
          warnings: [],
        },
      ],
    });

    const result = await generateText({
      model,
      prompt: "What is on example.com?",
      tools: spiderTools({ fetch: m.fetch, apiKey: "k" }),
      stopWhen: isStepCount(3),
    });

    assert.equal(result.text, "It is an example page.");
    assert.equal(m.calls.length, 1);
    assert.equal(m.calls[0].url, "https://api.spider.cloud/scrape");
    const toolResults = result.steps[0].toolResults;
    assert.equal(toolResults.length, 1);
    assert.deepEqual(toolResults[0].output, {
      url: "https://example.com",
      status: 200,
      content: "# Example Domain",
    });
  });

  it("rejects a crawl limit above maxPages before calling the API", async () => {
    const m = mockFetch();
    const t = spiderCrawl({ fetch: m.fetch, apiKey: "k", maxPages: 3 });
    const schema = t.inputSchema as unknown as { safeParse: (v: unknown) => { success: boolean } };
    assert.equal(schema.safeParse({ url: "https://example.com", limit: 4 }).success, false);
    assert.equal(schema.safeParse({ url: "https://example.com", limit: 3 }).success, true);
    assert.equal(schema.safeParse({ url: "not a url" }).success, false);
  });
});

describe("package", () => {
  it("VERSION matches package.json", () => {
    const pkg = JSON.parse(readFileSync(new URL("../package.json", import.meta.url), "utf8"));
    assert.equal(VERSION, pkg.version);
  });
});
