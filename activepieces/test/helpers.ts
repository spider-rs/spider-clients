import { AppConnectionType } from '@activepieces/shared';
import { createMockActionContext } from '@activepieces/pieces-framework';

export const TEST_KEY = 'sk-test-not-a-real-key';

export function secretAuth(key = TEST_KEY) {
  return { type: AppConnectionType.SECRET_TEXT, secret_text: key } as const;
}

/**
 * The framework mock context has no auth; actions read auth.secret_text, so
 * attach a SECRET_TEXT connection value the way the engine does.
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function contextFor(propsValue: Record<string, unknown>): any {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const ctx = createMockActionContext({ propsValue: propsValue as any });
  return { ...ctx, auth: secretAuth() };
}

/** Builds the object HttpError expects from axios for a failed response. */
export function axiosFailure(status: number, data: unknown = {}) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return { response: { status, data } } as any;
}
