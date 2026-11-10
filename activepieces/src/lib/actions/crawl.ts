import { createAction, Property } from '@activepieces/pieces-framework';
import { spiderAuth } from '../auth';
import {
  buildBody,
  extraParamsProp,
  requestTypeProp,
  returnFormatProp,
  spiderPost,
} from '../common';

export const crawlAction = createAction({
  auth: spiderAuth,
  name: 'crawl',
  displayName: 'Crawl site',
  description: 'Follow links from a starting URL and return one object per page.',
  audience: 'both',
  aiMetadata: {
    description:
      'Crawls a site from a starting URL and returns a JSON array with one page object per page (url, content, status, costs). Set limit to bound the crawl. Use Scrape for a single page and Links when only the URLs are needed.',
    idempotent: true,
  },
  props: {
    url: Property.ShortText({
      displayName: 'URL',
      description: 'Where the crawl starts.',
      required: true,
    }),
    limit: Property.Number({
      displayName: 'Page limit',
      description:
        'Maximum pages to crawl. 0 crawls every page found, capped by your remaining credit balance.',
      required: true,
      defaultValue: 10,
    }),
    depth: Property.Number({
      displayName: 'Depth',
      description: 'Maximum crawl depth. The API default is 25. 0 removes the limit.',
      required: false,
    }),
    return_format: returnFormatProp,
    request: requestTypeProp,
    extra: extraParamsProp,
  },
  async run({ auth, propsValue }) {
    const body = buildBody(
      {
        url: propsValue.url,
        limit: propsValue.limit,
        depth: propsValue.depth,
        return_format: propsValue.return_format,
        request: propsValue.request,
      },
      propsValue.extra,
    );
    return spiderPost(auth.secret_text, '/crawl', body);
  },
});
