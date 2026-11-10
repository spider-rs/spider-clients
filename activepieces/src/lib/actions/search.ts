import { createAction, Property } from '@activepieces/pieces-framework';
import { spiderAuth } from '../auth';
import { buildBody, extraParamsProp, returnFormatProp, spiderPost } from '../common';

export const searchAction = createAction({
  auth: spiderAuth,
  name: 'search',
  displayName: 'Search the web',
  description:
    'Return ranked results for a query. With Fetch page content on, fetch each result and return page objects instead.',
  audience: 'both',
  aiMetadata: {
    description:
      'Searches the web. Returns {content: [{title, description, url}]}, or with fetch_page_content true a JSON array of page objects with the content of each result.',
    idempotent: true,
  },
  props: {
    search: Property.ShortText({
      displayName: 'Query',
      description: 'What to search for.',
      required: true,
    }),
    search_limit: Property.Number({
      displayName: 'Result limit',
      description: 'How many results to fetch. 0 for all.',
      required: false,
      defaultValue: 5,
    }),
    fetch_page_content: Property.Checkbox({
      displayName: 'Fetch page content',
      description: 'Fetch the content of each result.',
      required: false,
      defaultValue: false,
    }),
    return_format: returnFormatProp,
    country: Property.ShortText({
      displayName: 'Country',
      description: 'Two letter country code, for example us.',
      required: false,
    }),
    language: Property.ShortText({
      displayName: 'Language',
      description: 'Two letter language code, for example en.',
      required: false,
    }),
    tbs: Property.StaticDropdown({
      displayName: 'Time range',
      required: false,
      options: {
        disabled: false,
        options: [
          { label: 'Past hour', value: 'qdr:h' },
          { label: 'Past day', value: 'qdr:d' },
          { label: 'Past week', value: 'qdr:w' },
          { label: 'Past month', value: 'qdr:m' },
          { label: 'Past year', value: 'qdr:y' },
        ],
      },
    }),
    extra: extraParamsProp,
  },
  async run({ auth, propsValue }) {
    const fetchContent = propsValue.fetch_page_content === true;
    const body = buildBody(
      {
        search: propsValue.search,
        search_limit: propsValue.search_limit,
        fetch_page_content: fetchContent,
        return_format: fetchContent ? propsValue.return_format : undefined,
        country: propsValue.country,
        language: propsValue.language,
        tbs: propsValue.tbs,
      },
      propsValue.extra,
    );
    return spiderPost(auth.secret_text, '/search', body);
  },
});
