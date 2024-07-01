import { describe, test, expect, jest } from "@jest/globals";
import { Spider } from "../src";

jest.setTimeout(1000 * 60);

describe("Spider JS SDK", () => {
  test("should throw error if API key is not provided", () => {
    expect(() => new Spider({ apiKey: undefined })).toThrow(
      "No API key provided"
    );
  });
  test("should scrape url with data", async () => {
    await import("dotenv/config");

    if (process.env.SPIDER_API_KEY) {
      const spiderClient = new Spider({ apiKey: process.env.SPIDER_API_KEY });
      const spiderData = await spiderClient.scrapeUrl("https://spider.cloud", {
        store_data: true,
      });

      expect(Array.isArray(spiderData));
    }
  });
  test("should get data from the api", async () => {
    await import("dotenv/config");

    if (process.env.SPIDER_API_KEY) {
      const spiderClient = new Spider({ apiKey: process.env.SPIDER_API_KEY });
      const spiderData = await spiderClient.getData("websites", { limit: 1 });

      expect(Array.isArray(spiderData));
    }
  });
  test("should download data from the api", async () => {
    await import("dotenv/config");

    if (process.env.SPIDER_API_KEY) {
      const spiderClient = new Spider({ apiKey: process.env.SPIDER_API_KEY });
      const spiderData = await spiderClient.createSignedUrl("spider.cloud", {
        limit: 1,
        page: 0,
      });

      expect(spiderData);
    }
  });

  test("should connect with supabase", async () => {
    await import("dotenv/config");

    if (process.env.SPIDER_API_KEY) {
      const spiderClient = new Spider({ apiKey: process.env.SPIDER_API_KEY });
      await spiderClient.init_supabase();

      const auth = await spiderClient.supabase?.auth.signInWithPassword({
        email: process.env.SPIDER_EMAIL || "",
        password: process.env.SPIDER_PASSWORD || "",
      });

      expect(auth);
    }
  });
});
