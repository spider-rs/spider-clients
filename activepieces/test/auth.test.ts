import { httpClient, HttpError, HttpMethod } from '@activepieces/pieces-common';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { validateSpiderKey } from '../src/lib/auth';
import { axiosFailure, TEST_KEY } from './helpers';

const sendRequest = vi.spyOn(httpClient, 'sendRequest');

beforeEach(() => {
  sendRequest.mockReset();
});

describe('validateSpiderKey', () => {
  it('checks the key with GET /data/credits, which spends nothing', async () => {
    sendRequest.mockResolvedValue({ status: 200, headers: {}, body: { data: { credits: 10 } } });
    await expect(validateSpiderKey(TEST_KEY)).resolves.toEqual({ valid: true });
    expect(sendRequest).toHaveBeenCalledTimes(1);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const req = sendRequest.mock.calls[0][0] as any;
    expect(req.method).toBe(HttpMethod.GET);
    expect(req.url).toBe('https://api.spider.cloud/data/credits');
    expect(req.headers.Authorization).toBe(`Bearer ${TEST_KEY}`);
    expect(req.body).toBeUndefined();
  });

  it('rejects a key the API answers with 401', async () => {
    sendRequest.mockRejectedValue(new HttpError(undefined, axiosFailure(401)));
    await expect(validateSpiderKey('bad')).resolves.toEqual({
      valid: false,
      error: 'Invalid API key.',
    });
  });

  it('accepts a known key on an account with no credits (402)', async () => {
    sendRequest.mockRejectedValue(new HttpError(undefined, axiosFailure(402)));
    await expect(validateSpiderKey(TEST_KEY)).resolves.toEqual({ valid: true });
  });

  it('reports other failures without accepting the key', async () => {
    sendRequest.mockRejectedValue(new HttpError(undefined, axiosFailure(503)));
    const result = await validateSpiderKey(TEST_KEY);
    expect(result.valid).toBe(false);
  });
});
