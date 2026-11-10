import { createCustomApiCallAction } from '@activepieces/pieces-common';
import { createPiece } from '@activepieces/pieces-framework';
import { PieceCategory } from '@activepieces/shared';
import { crawlAction } from './lib/actions/crawl';
import { linksAction } from './lib/actions/links';
import { scrapeAction } from './lib/actions/scrape';
import { searchAction } from './lib/actions/search';
import { spiderAuth } from './lib/auth';
import { authHeaders, SPIDER_API_BASE_URL } from './lib/common';

export { spiderAuth } from './lib/auth';

export const spider = createPiece({
  displayName: 'Spider',
  description: 'Scrape, crawl and search the web with the Spider API. Returns Markdown, text or HTML.',
  logoUrl: 'https://spider.cloud/apple-touch-icon.png',
  minimumSupportedRelease: '0.82.0',
  categories: [PieceCategory.ARTIFICIAL_INTELLIGENCE, PieceCategory.PRODUCTIVITY],
  authors: ['spider-rs'],
  auth: spiderAuth,
  actions: [
    scrapeAction,
    crawlAction,
    searchAction,
    linksAction,
    createCustomApiCallAction({
      auth: spiderAuth,
      baseUrl: () => SPIDER_API_BASE_URL,
      authMapping: async (auth) => authHeaders(auth.secret_text),
      props: {
        url: {
          description: `Full URL, or a path relative to ${SPIDER_API_BASE_URL}, for example /data/credits`,
        },
      },
    }),
  ],
  triggers: [],
});
