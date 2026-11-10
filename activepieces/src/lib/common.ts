import { httpClient, HttpMethod } from '@activepieces/pieces-common';
import { Property } from '@activepieces/pieces-framework';

export const SPIDER_API_BASE_URL = 'https://api.spider.cloud';

export const SPIDER_USER_AGENT = 'Spider-Activepieces/0.1.0';

export function authHeaders(apiKey: string): Record<string, string> {
  return {
    Authorization: `Bearer ${apiKey}`,
    'User-Agent': SPIDER_USER_AGENT,
  };
}

/**
 * Drops keys whose value is undefined, null or an empty string, so the API
 * applies its own defaults for every field the user left blank.
 */
export function compact(input: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(input)) {
    if (value === undefined || value === null || value === '') {
      continue;
    }
    out[key] = value;
  }
  return out;
}

/**
 * Builds the JSON body: the extra parameters first, then the named fields,
 * so a field set in the form always wins over the same key in the JSON.
 */
export function buildBody(
  fields: Record<string, unknown>,
  extra: unknown,
): Record<string, unknown> {
  const extraObject =
    extra && typeof extra === 'object' && !Array.isArray(extra)
      ? (extra as Record<string, unknown>)
      : {};
  return { ...compact(extraObject), ...compact(fields) };
}

export async function spiderPost(
  apiKey: string,
  path: string,
  body: Record<string, unknown>,
): Promise<unknown> {
  const response = await httpClient.sendRequest({
    method: HttpMethod.POST,
    url: `${SPIDER_API_BASE_URL}${path}`,
    headers: {
      ...authHeaders(apiKey),
      'Content-Type': 'application/json',
    },
    body,
  });
  return response.body;
}

export const returnFormatProp = Property.StaticDropdown({
  displayName: 'Return format',
  description: 'Output format for each page. Markdown suits LLM input. Raw is the unmodified HTML.',
  required: false,
  defaultValue: 'markdown',
  options: {
    disabled: false,
    options: [
      { label: 'Markdown', value: 'markdown' },
      { label: 'CommonMark', value: 'commonmark' },
      { label: 'Text', value: 'text' },
      { label: 'HTML to text', value: 'html2text' },
      { label: 'Raw HTML', value: 'raw' },
      { label: 'XML', value: 'xml' },
    ],
  },
});

export const requestTypeProp = Property.StaticDropdown({
  displayName: 'Request type',
  description:
    'How to fetch. Smart, the default, tries HTTP and moves to a browser only when the page needs it. HTTP runs no JavaScript. Browser renders the page.',
  required: false,
  defaultValue: 'smart',
  options: {
    disabled: false,
    options: [
      { label: 'Smart', value: 'smart' },
      { label: 'HTTP', value: 'http' },
      { label: 'Browser', value: 'browser' },
    ],
  },
});

export const extraParamsProp = Property.Json({
  displayName: 'Additional parameters',
  description:
    'Any other request parameters from https://spider.cloud/docs/api as a JSON object, for example {"readability": true}. Fields set above take precedence.',
  required: false,
});
