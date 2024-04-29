import { describe, test, expect, jest } from '@jest/globals';
import Spider from "../src/spiderwebai";

jest.setTimeout(1000 * 60)

describe("Spider JS SDK", () => {
  test("should throw error if API key is not provided", () => {
    expect(() => new Spider({ apiKey: undefined })).toThrow("No API key provided");
  });
  test("should get data from the api", async () => {
    await import("dotenv/config")

    if (process.env.SPIDER_API_KEY) {
      const spiderClient = new Spider({ apiKey: process.env.SPIDER_API_KEY });
      const spiderData = await spiderClient.scrapeUrl("https://spider.cloud");

      expect(Array.isArray(spiderData))
    }
  });
});
