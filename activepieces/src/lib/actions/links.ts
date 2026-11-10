import { createAction, Property } from '@activepieces/pieces-framework';
import { spiderAuth } from '../auth';
import { buildBody, extraParamsProp, requestTypeProp, spiderPost } from '../common';

export const linksAction = createAction({
  auth: spiderAuth,
  name: 'links',
  displayName: 'Collect links',
  description: 'Crawl like Crawl site and return the URLs found on each page instead of the content.',
  audience: 'both',
  aiMetadata: {
    description:
      'Crawls a site from a starting URL and returns a JSON array with one object per page, each with a links array. Use it to map a site before scraping chosen pages.',
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
    request: requestTypeProp,
    extra: extraParamsProp,
  },
  async run({ auth, propsValue }) {
    const body = buildBody(
      {
        url: propsValue.url,
        limit: propsValue.limit,
        depth: propsValue.depth,
        request: propsValue.request,
      },
      propsValue.extra,
    );
    return spiderPost(auth.secret_text, '/links', body);
  },
});
