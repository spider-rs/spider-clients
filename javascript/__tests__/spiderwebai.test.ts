import { describe, test } from "node:test";
import assert from "node:assert";
import { Spider } from "../src";
import "dotenv/config";

describe("Spider JS SDK", () => {
  test("should throw error if API key is not provided", () => {
    if (!process.env.SPIDER_API_KEY) {
      assert.throws(() => new Spider({ apiKey: null }));
    } else {
      assert.doesNotThrow(() => new Spider({ apiKey: null }));
    }
  });

  test("should crawl url with data", async () => {
    const spiderClient = new Spider();
    const spiderData = await spiderClient.crawlUrl("https://spider.cloud", {
      store_data: true,
      limit: 2,
    });

    assert(Array.isArray(spiderData));
    assert(spiderData && spiderData.length === 2);
  });

  test("should crawl url streaming with data", async () => {
    const stream = true;

    const spiderClient = new Spider();
    const spiderData = await spiderClient.crawlUrl(
      "https://spider.cloud",
      {
        store_data: true,
        limit: 4,
      },
      stream,
      (data) => {
        assert(data["url"]);
      }
    );

    assert(typeof spiderData === "undefined");
  });

  test("should scrape url with data", async () => {
    const spiderClient = new Spider();
    const spiderData = await spiderClient.scrapeUrl("https://spider.cloud", {
      store_data: true,
    });

    assert(Array.isArray(spiderData));
  });

  test("should get data from the api", async () => {
    const spiderClient = new Spider();
    const { data } = await spiderClient.getData("websites", { limit: 1 });

    assert(Array.isArray(data));
  });

  // test.skip("should download data from the api", async () => {
  //   await import("dotenv/config");

  //   const spiderClient = new Spider();
  //   const spiderData = await spiderClient.createSignedUrl("spider.cloud", {
  //     limit: 1,
  //     page: 0,
  //   });

  //   assert(spiderData);
  // });

  test("should connect with supabase", async () => {
    const spiderClient = new Spider();
    await spiderClient.init_supabase();

    const auth = await spiderClient.supabase?.auth.signInWithPassword({
      email: process.env.SPIDER_EMAIL || "",
      password: process.env.SPIDER_PASSWORD || "",
    });

    assert(auth);
  });
});
