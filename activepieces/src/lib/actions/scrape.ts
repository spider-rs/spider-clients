import { createAction, Property } from '@activepieces/pieces-framework';
import { spiderAuth } from '../auth';
import {
  buildBody,
  extraParamsProp,
  requestTypeProp,
  returnFormatProp,
  spiderPost,
} from '../common';

export const scrapeAction = createAction({
  auth: spiderAuth,
  name: 'scrape',
  displayName: 'Scrape page',
  description: 'Fetch one page and return its content as Markdown, text or HTML.',
  audience: 'both',
  aiMetadata: {
    description:
      'Fetches a single URL and returns a JSON array with one page object (url, content, status, costs). Use it to read one known page. Use Crawl for a whole site and Search to find pages by query.',
    idempotent: true,
  },
  props: {
    url: Property.ShortText({
      displayName: 'URL',
      description: 'The page to fetch.',
      required: true,
    }),
    return_format: returnFormatProp,
    request: requestTypeProp,
    readability: Property.Checkbox({
      displayName: 'Readability',
      description: 'Strip boilerplate before converting.',
      required: false,
    }),
    root_selector: Property.ShortText({
      displayName: 'Root selector',
      description: 'CSS selector for the part of the page to extract, for example #content.',
      required: false,
    }),
    extra: extraParamsProp,
  },
  async run({ auth, propsValue }) {
    const body = buildBody(
      {
        url: propsValue.url,
        return_format: propsValue.return_format,
        request: propsValue.request,
        readability: propsValue.readability || undefined,
        root_selector: propsValue.root_selector,
      },
      propsValue.extra,
    );
    return spiderPost(auth.secret_text, '/scrape', body);
  },
});
