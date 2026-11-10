import { tool } from "ai";
import { z } from "zod";
import {
  asPages,
  compactPage,
  spiderPost,
  type SpiderPage,
  type SpiderSearchResult,
  type SpiderToolsConfig,
} from "./client.js";

/**
 * Request fields passed through to the Spider API on every call.
 * The model's own arguments win over these. Full list:
 * https://spider.cloud/openapi.yaml
 */
export interface SpiderRequestParams {
  return_format?: "markdown" | "commonmark" | "text" | "raw" | "xml" | "html2text";
  request?: "smart" | "http" | "browser";
  readability?: boolean;
  root_selector?: string;
  exclude_selector?: string;
  stealth?: boolean;
  metadata?: boolean;
  locale?: string;
  cache?: boolean;
  request_timeout?: number;
  [key: string]: unknown;
}

export interface SpiderToolOptions extends SpiderToolsConfig {
  /** Extra Spider API fields sent with every call from this tool. */
  params?: SpiderRequestParams;
}

export interface SpiderCrawlToolOptions extends SpiderToolOptions {
  /** Largest page limit the model may ask for. Defaults to 20. */
  maxPages?: number;
}

export interface SpiderSearchToolOptions extends SpiderToolOptions {
  /** Largest result count the model may ask for. Defaults to 10. */
  maxResults?: number;
}

const returnFormat = z
  .enum(["markdown", "text", "raw"])
  .optional()
  .describe("Output format. markdown suits most uses. raw is the page HTML.");

const requestMode = z
  .enum(["smart", "http", "browser"])
  .optional()
  .describe(
    "How to fetch. smart (default) uses plain HTTP and switches to a browser when the page needs JavaScript. browser always renders.",
  );

const urlInput = z.string().url().describe("Absolute URL of the page, starting with http:// or https://");

/** Scrape one page into markdown or text. Works without an API key on the rate limited keyless tier. */
export function spiderScrape(options: SpiderToolOptions = {}) {
  const { params, ...config } = options;
  return tool({
    description:
      "Fetch one web page and return its content as markdown or text. Use it to read a page whose URL you already know.",
    inputSchema: z.object({
      url: urlInput,
      return_format: returnFormat,
      request: requestMode,
    }),
    execute: async (input, options) => {
      const abortSignal = options?.abortSignal;
      const data = await spiderPost<unknown>(
        config,
        "scrape",
        { return_format: "markdown", ...params, ...input },
        { abortSignal },
      );
      const [page] = asPages(data);
      return page ? compactPage(page, config.maxContentChars) : { url: input.url, content: null };
    },
  });
}

/** Crawl a site from a start URL and return one entry per page. Needs an API key. */
export function spiderCrawl(options: SpiderCrawlToolOptions = {}) {
  const { params, maxPages = 20, ...config } = options;
  return tool({
    description:
      "Crawl a website from a start URL, following its links, and return the content of each page found. Use it to read several pages of one site.",
    inputSchema: z.object({
      url: urlInput,
      limit: z
        .number()
        .int()
        .min(1)
        .max(maxPages)
        .optional()
        .describe(`Maximum pages to crawl, from 1 to ${maxPages}. Defaults to 5.`),
      depth: z.number().int().min(1).max(25).optional().describe("Maximum link depth from the start URL."),
      return_format: returnFormat,
      request: requestMode,
    }),
    execute: async (input, options) => {
      const abortSignal = options?.abortSignal;
      const data = await spiderPost<unknown>(
        config,
        "crawl",
        { return_format: "markdown", ...params, limit: 5, ...input },
        { requireKey: true, abortSignal },
      );
      return asPages(data).map((p) => compactPage(p, config.maxContentChars));
    },
  });
}

/** Search the web. Optionally fetch each result's page content. Needs an API key. */
export function spiderSearch(options: SpiderSearchToolOptions = {}) {
  const { params, maxResults = 10, ...config } = options;
  return tool({
    description:
      "Search the web and return ranked results with title, description and URL. Set fetch_page_content to also get each result's page content.",
    inputSchema: z.object({
      query: z.string().min(1).describe("The search query."),
      search_limit: z
        .number()
        .int()
        .min(1)
        .max(maxResults)
        .optional()
        .describe(`How many results to return, from 1 to ${maxResults}. Defaults to 5.`),
      fetch_page_content: z
        .boolean()
        .optional()
        .describe("Fetch the content of each result page. Slower and uses more credits."),
      country: z.string().length(2).optional().describe("Two letter country code, for example us."),
      language: z.string().length(2).optional().describe("Two letter language code, for example en."),
      tbs: z
        .enum(["qdr:h", "qdr:d", "qdr:w", "qdr:m", "qdr:y"])
        .optional()
        .describe("Time range: past hour, day, week, month or year."),
    }),
    execute: async (input, options) => {
      const abortSignal = options?.abortSignal;
      const { query, ...rest } = input;
      const data = await spiderPost<unknown>(
        config,
        "search",
        {
          ...(rest.fetch_page_content ? { return_format: "markdown" } : {}),
          ...params,
          search_limit: 5,
          ...rest,
          search: query,
        },
        { requireKey: true, abortSignal },
      );
      if (Array.isArray(data)) {
        return { pages: (data as SpiderPage[]).map((p) => compactPage(p, config.maxContentChars)) };
      }
      const content = (data as { content?: SpiderSearchResult[] } | null)?.content;
      return {
        results: Array.isArray(content)
          ? content.map(({ title, description, url }) => ({ title, description, url }))
          : [],
      };
    },
  });
}

/** Collect the links found on a page or across a crawl. Needs an API key. */
export function spiderLinks(options: SpiderCrawlToolOptions = {}) {
  const { params, maxPages = 20, ...config } = options;
  return tool({
    description:
      "List the URLs linked from a page, or from each page of a short crawl. Use it to map a site before reading pages.",
    inputSchema: z.object({
      url: urlInput,
      limit: z
        .number()
        .int()
        .min(1)
        .max(maxPages)
        .optional()
        .describe(`Maximum pages to visit, from 1 to ${maxPages}. Defaults to 1, the start page only.`),
    }),
    execute: async (input, options) => {
      const abortSignal = options?.abortSignal;
      const data = await spiderPost<unknown>(
        config,
        "links",
        { ...params, limit: 1, ...input },
        { requireKey: true, abortSignal },
      );
      return asPages(data).map((p) => ({
        url: p.url,
        status: p.status,
        ...(p.error ? { error: p.error } : {}),
        links: Array.isArray(p.links) ? p.links : [],
      }));
    },
  });
}

/** All four Spider tools, keyed for `generateText({ tools })`. */
export function spiderTools(options: SpiderCrawlToolOptions & SpiderSearchToolOptions = {}) {
  return {
    scrape: spiderScrape(options),
    crawl: spiderCrawl(options),
    search: spiderSearch(options),
    links: spiderLinks(options),
  };
}
