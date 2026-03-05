export { Spider } from "./client";
export {
  Collection,
  setBaseUrl,
  APISchema,
  AI_STUDIO_RATE_LIMITS,
  AIStudioInfo,
  AIStudioSubscriptionRequired,
  AIStudioRateLimitExceeded,
} from "./config";
export type {
  SpiderParams,
  Budget,
  Viewport,
  QueryRequest,
  AIRequestParams,
  AIStudioTier,
} from "./config";
// Browser automation
export { SpiderBrowser, SpiderPage } from "spider-browser";
export type { SpiderBrowserOptions, SpiderEvents } from "spider-browser";

// Browser AI
export { Agent, act, observe, extract } from "spider-browser";
export type { AgentOptions, AgentResult, ObserveResult } from "spider-browser";

// Browser retry & stealth
export { RetryEngine } from "spider-browser";
export type { RetryOptions } from "spider-browser";
