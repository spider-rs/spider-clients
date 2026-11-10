import { httpClient, HttpError, HttpMethod } from '@activepieces/pieces-common';
import { PieceAuth } from '@activepieces/pieces-framework';
import { authHeaders, SPIDER_API_BASE_URL } from './common';

const description = `
To get your Spider API key:

1. Sign in at [spider.cloud](https://spider.cloud/api-keys?utm_source=activepieces&utm_medium=directory&utm_campaign=activepieces-listing).
2. Create a key on the API keys page and paste it here.
`;

/**
 * Checks a key with GET /data/credits, which reads the balance and spends nothing.
 * 200 means the key works. 402 means the key is known but the account has no
 * credits, so the connection is still saved. Anything else is rejected.
 */
export async function validateSpiderKey(
  apiKey: string,
): Promise<{ valid: true } | { valid: false; error: string }> {
  try {
    await httpClient.sendRequest({
      method: HttpMethod.GET,
      url: `${SPIDER_API_BASE_URL}/data/credits`,
      headers: authHeaders(apiKey),
    });
    return { valid: true };
  } catch (e) {
    const status = e instanceof HttpError ? e.response.status : undefined;
    if (status === 402) {
      return { valid: true };
    }
    if (status === 401 || status === 403) {
      return { valid: false, error: 'Invalid API key.' };
    }
    return {
      valid: false,
      error: `Could not check the key${status ? ` (HTTP ${status})` : ''}. Try again.`,
    };
  }
}

export const spiderAuth = PieceAuth.SecretText({
  displayName: 'API key',
  description,
  required: true,
  validate: async ({ auth }) => validateSpiderKey(auth),
});
