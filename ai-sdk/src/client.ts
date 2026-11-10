export const VERSION = "0.1.0";

export const DEFAULT_BASE_URL = "https://api.spider.cloud";

/** Settings shared by every Spider tool. */
export interface SpiderToolsConfig {
  /**
   * Spider API key. Defaults to the `SPIDER_API_KEY` environment variable.
   * `scrape` also answers without a key, on a rate limited keyless tier.
   * `crawl`, `search` and `links` need a key.
   */
  apiKey?: string;
  /** API base URL. Defaults to https://api.spider.cloud. */
  baseUrl?: string;
  /** Custom fetch implementation, for tests or proxies. Defaults to the global fetch. */
  fetch?: typeof globalThis.fetch;
  /** Extra headers sent with every request. */
  headers?: Record<string, string>;
  /**
   * Cut each page's content to this many characters before it reaches the model.
   * Unset keeps the full content.
   */
  maxContentChars?: number;
}

/** One page as returned by /scrape, /crawl and /links. */
export interface SpiderPage {
  url?: string;
  content?: string | null;
  status?: number;
  error?: string | null;
  links?: string[];
  metadata?: Record<string, unknown> | null;
  [key: string]: unknown;
}

/** One ranked result from /search when page content is not fetched. */
export interface SpiderSearchResult {
  title?: string;
  description?: string;
  url?: string;
}

/** Error thrown when the Spider API answers with a non 2xx status. */
export class SpiderApiError extends Error {
  readonly status: number;
  readonly retryAfter?: number;
  readonly body: string;

  constructor(route: string, status: number, body: string, retryAfter?: number) {
    const hint =
      status === 401 || status === 402
        ? " Set SPIDER_API_KEY to a key from https://spider.cloud/api-keys."
        : status === 429 && retryAfter !== undefined
          ? ` Retry after ${retryAfter}s.`
          : "";
    super(`Spider ${route} failed with ${status}: ${body.slice(0, 500)}${hint}`);
    this.name = "SpiderApiError";
    this.status = status;
    this.body = body;
    this.retryAfter = retryAfter;
  }
}

function readEnvKey(): string | undefined {
  const env = (globalThis as { process?: { env?: Record<string, string | undefined> } })
    .process?.env;
  return env?.SPIDER_API_KEY || undefined;
}

export interface SpiderRequestOptions {
  /** Throw before sending when no API key is set. */
  requireKey?: boolean;
  abortSignal?: AbortSignal;
}

/** POST a JSON body to a Spider route and return the parsed JSON. */
export async function spiderPost<T>(
  config: SpiderToolsConfig,
  route: string,
  body: Record<string, unknown>,
  options: SpiderRequestOptions = {},
): Promise<T> {
  const apiKey = config.apiKey ?? readEnvKey();
  if (options.requireKey && !apiKey) {
    throw new Error(
      `Spider /${route} needs an API key. Set SPIDER_API_KEY or pass apiKey. Get one at https://spider.cloud/api-keys.`,
    );
  }
  const doFetch = config.fetch ?? globalThis.fetch;
  const base = (config.baseUrl ?? DEFAULT_BASE_URL).replace(/\/+$/, "");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "User-Agent": `spider-ai-sdk/${VERSION}`,
    ...config.headers,
  };
  if (apiKey) {
    headers.Authorization = `Bearer ${apiKey}`;
  }

  const res = await doFetch(`${base}/${route}`, {
    method: "POST",
    headers,
    body: JSON.stringify(dropUndefined(body)),
    signal: options.abortSignal,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    const retry = res.headers.get("Retry-After");
    const retryAfter = retry !== null && retry !== "" ? Number(retry) : undefined;
    throw new SpiderApiError(
      `/${route}`,
      res.status,
      text,
      retryAfter !== undefined && Number.isFinite(retryAfter) ? retryAfter : undefined,
    );
  }
  return (await res.json()) as T;
}

function dropUndefined(body: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(body)) {
    if (v !== undefined) out[k] = v;
  }
  return out;
}

/** Keep the fields a model needs and cut long content. */
export function compactPage(page: SpiderPage, maxContentChars?: number): SpiderPage {
  const out: SpiderPage = { url: page.url, status: page.status };
  if (page.error) out.error = page.error;
  if (typeof page.content === "string") {
    out.content =
      maxContentChars !== undefined && page.content.length > maxContentChars
        ? page.content.slice(0, maxContentChars)
        : page.content;
  }
  if (Array.isArray(page.links)) out.links = page.links;
  if (page.metadata) out.metadata = page.metadata;
  return out;
}

export function asPages(data: unknown): SpiderPage[] {
  if (Array.isArray(data)) return data as SpiderPage[];
  if (data && typeof data === "object") return [data as SpiderPage];
  return [];
}
