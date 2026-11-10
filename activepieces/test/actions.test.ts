import { httpClient, HttpError, HttpMethod } from '@activepieces/pieces-common';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { spider } from '../src';
import { crawlAction } from '../src/lib/actions/crawl';
import { linksAction } from '../src/lib/actions/links';
import { scrapeAction } from '../src/lib/actions/scrape';
import { searchAction } from '../src/lib/actions/search';
import { axiosFailure, contextFor, TEST_KEY } from './helpers';

const sendRequest = vi.spyOn(httpClient, 'sendRequest');

function reply(body: unknown) {
  sendRequest.mockResolvedValue({ status: 200, headers: {}, body });
}

function lastRequest() {
  expect(sendRequest).toHaveBeenCalledTimes(1);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return sendRequest.mock.calls[0][0] as any;
}

beforeEach(() => {
  sendRequest.mockReset();
});

afterEach(() => {
  sendRequest.mockReset();
});

describe('piece definition', () => {
  it('exposes scrape, crawl, search, links and the custom API call', () => {
    expect(Object.keys(spider.actions()).sort()).toEqual(
      ['crawl', 'custom_api_call', 'links', 'scrape', 'search'].sort(),
    );
    expect(spider.displayName).toBe('Spider');
    expect(spider.metadata().auth).toBeDefined();
  });
});

describe('scrape', () => {
  it('posts to /scrape with bearer auth and drops blank fields', async () => {
    const pages = [{ url: 'https://example.com', content: '# Example', status: 200 }];
    reply(pages);

    const result = await scrapeAction.run(
      contextFor({
        url: 'https://example.com',
        return_format: 'markdown',
        request: 'smart',
        readability: false,
        root_selector: '',
        extra: undefined,
      }),
    );

    expect(result).toEqual(pages);
    const req = lastRequest();
    expect(req.method).toBe(HttpMethod.POST);
    expect(req.url).toBe('https://api.spider.cloud/scrape');
    expect(req.headers.Authorization).toBe(`Bearer ${TEST_KEY}`);
    expect(req.headers['Content-Type']).toBe('application/json');
    expect(req.body).toEqual({
      url: 'https://example.com',
      return_format: 'markdown',
      request: 'smart',
    });
  });

  it('merges additional parameters, with form fields taking precedence', async () => {
    reply([]);
    await scrapeAction.run(
      contextFor({
        url: 'https://example.com',
        return_format: 'text',
        readability: true,
        extra: { metadata: true, return_format: 'raw', cookies: '' },
      }),
    );
    expect(lastRequest().body).toEqual({
      url: 'https://example.com',
      return_format: 'text',
      readability: true,
      metadata: true,
    });
  });

  it('ignores additional parameters that are not a JSON object', async () => {
    reply([]);
    await scrapeAction.run(contextFor({ url: 'https://example.com', extra: ['x'] }));
    expect(lastRequest().body).toEqual({ url: 'https://example.com' });
  });

  it('surfaces API errors', async () => {
    sendRequest.mockRejectedValue(new HttpError({}, axiosFailure(402, { error: 'out of credits' })));
    await expect(scrapeAction.run(contextFor({ url: 'https://example.com' }))).rejects.toBeInstanceOf(
      HttpError,
    );
  });
});

describe('crawl', () => {
  it('posts to /crawl with limit and depth', async () => {
    reply([{ url: 'https://example.com' }, { url: 'https://example.com/about' }]);
    const result = await crawlAction.run(
      contextFor({
        url: 'https://example.com',
        limit: 10,
        depth: 2,
        return_format: 'markdown',
        request: 'http',
      }),
    );
    expect(result).toHaveLength(2);
    const req = lastRequest();
    expect(req.url).toBe('https://api.spider.cloud/crawl');
    expect(req.body).toEqual({
      url: 'https://example.com',
      limit: 10,
      depth: 2,
      return_format: 'markdown',
      request: 'http',
    });
  });

  it('keeps a limit of 0, which the API reads as no page cap', async () => {
    reply([]);
    await crawlAction.run(contextFor({ url: 'https://example.com', limit: 0 }));
    expect(lastRequest().body).toEqual({ url: 'https://example.com', limit: 0 });
  });
});

describe('links', () => {
  it('posts to /links without a return format', async () => {
    reply([{ url: 'https://example.com', links: ['https://example.com/a'] }]);
    await linksAction.run(contextFor({ url: 'https://example.com', limit: 5 }));
    const req = lastRequest();
    expect(req.url).toBe('https://api.spider.cloud/links');
    expect(req.body).toEqual({ url: 'https://example.com', limit: 5 });
  });
});

describe('search', () => {
  it('posts the query as search and leaves out return_format for result lists', async () => {
    const results = { content: [{ title: 'Spider', description: 'x', url: 'https://spider.cloud' }] };
    reply(results);
    const result = await searchAction.run(
      contextFor({
        search: 'rust web crawler',
        search_limit: 5,
        fetch_page_content: false,
        return_format: 'markdown',
        country: 'us',
        language: '',
        tbs: 'qdr:w',
      }),
    );
    expect(result).toEqual(results);
    const req = lastRequest();
    expect(req.url).toBe('https://api.spider.cloud/search');
    expect(req.body).toEqual({
      search: 'rust web crawler',
      search_limit: 5,
      fetch_page_content: false,
      country: 'us',
      tbs: 'qdr:w',
    });
  });

  it('sends return_format when page content is fetched', async () => {
    reply([]);
    await searchAction.run(
      contextFor({ search: 'spider', fetch_page_content: true, return_format: 'text' }),
    );
    expect(lastRequest().body).toEqual({
      search: 'spider',
      fetch_page_content: true,
      return_format: 'text',
    });
  });
});

describe('custom API call', () => {
  it('resolves a relative path against the API and adds bearer auth', async () => {
    reply({ data: { credits: 1 } });
    const action = spider.getAction('custom_api_call');
    expect(action).toBeDefined();
    await action!.run(
      contextFor({
        method: HttpMethod.GET,
        url: { url: '/data/credits' },
        headers: {},
        queryParams: {},
        body_type: 'none',
        failsafe: false,
      }),
    );
    const req = lastRequest();
    expect(req.method).toBe(HttpMethod.GET);
    expect(req.url).toBe('https://api.spider.cloud/data/credits');
    expect(req.headers.Authorization).toBe(`Bearer ${TEST_KEY}`);
  });
});
