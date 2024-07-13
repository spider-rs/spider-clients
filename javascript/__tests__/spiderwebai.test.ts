import { describe, test } from "node:test";
import assert from "node:assert";
import { Spider } from "../src";
import "dotenv/config";
import { GenericParams } from "../src/client";

describe("Spider JS SDK", () => {
  const url = "https://example.com";
  const params: GenericParams = {
    limit: 1,
    return_format: "markdown",
    depth: 2,
    cache: true,
  };

  test("should throw error if API key is not provided", () => {
    if (!process.env.SPIDER_API_KEY) {
      assert.throws(() => new Spider({ apiKey: null }));
    } else {
      assert.doesNotThrow(() => new Spider({ apiKey: null }));
    }
  });

  test("should scrape url with data", async () => {
    const spiderClient = new Spider();
    const spiderData = await spiderClient.scrapeUrl(url, params);

    assert(Array.isArray(spiderData));
    assert(spiderData.length > 0);
    assert(spiderData[0].content);
    assert(spiderData[0].error !== undefined);
    assert(spiderData[0].status);
    assert(spiderData[0].url);
  });

  test("should crawl url with data", async () => {
    const spiderClient = new Spider();
    const spiderData = await spiderClient.crawlUrl(url, params);

    assert(Array.isArray(spiderData));
    assert(spiderData.length > 0);
    assert(spiderData[0].content);
    assert(spiderData[0].error !== undefined);
    assert(spiderData[0].status);
    assert(spiderData[0].url);
  });

  test("should get links", async () => {
    const spiderClient = new Spider();
    const linksData = await spiderClient.links(url, params);

    assert(Array.isArray(linksData));
    assert(linksData.length > 0);
    assert(linksData[0].error !== undefined);
    assert(linksData[0].status);
    assert(linksData[0].url);
  });

  test("should take screenshot", async () => {
    const spiderClient = new Spider();
    const screenshotData = await spiderClient.screenshot(url, { limit: 1 });

    assert(Array.isArray(screenshotData));
  });

  test("should perform search", async () => {
    const spiderClient = new Spider();
    const searchData = await spiderClient.search(
      "example search query",
      params
    );

    assert(Array.isArray(searchData));
    assert(searchData.length > 0);
    assert(searchData[0].content);
    assert(searchData[0].error !== undefined);
    assert(searchData[0].status);
    assert(searchData[0].url);
  });

  test("should transform data", async () => {
    const spiderClient = new Spider();
    const transformData = [
      { html: "<html><body>Example</body></html>", url: url },
    ];
    const transformedData = await spiderClient.transform(transformData, params);

    assert(typeof transformedData === "object");
    assert(transformedData.content);
    assert(transformedData.error !== undefined);
    assert(transformedData.status);
  });

  test("should extract contacts", async () => {
    const spiderClient = new Spider();
    const contactsData = await spiderClient.extractContacts(url, params);

    assert(Array.isArray(contactsData));
    assert(contactsData.length > 0);
    assert(contactsData[0].content);
    assert(contactsData[0].error !== undefined);
    assert(contactsData[0].status);
    assert(contactsData[0].url);
  });

  test("should label data", async () => {
    const spiderClient = new Spider();
    const labelData = await spiderClient.label(url, params);

    assert(Array.isArray(labelData));
    assert(labelData.length > 0);
    assert(labelData[0].content);
    assert(labelData[0].error !== undefined);
    assert(labelData[0].status);
    assert(labelData[0].url);
  });

  test("should get crawl state", async () => {
    const spiderClient = new Spider();
    const crawlState = await spiderClient.getCrawlState(url, params);

    assert(typeof crawlState === "object");
    assert(Array.isArray(crawlState.data));
  });

  test("should query global db", async () => {
    const spiderClient = new Spider();
    const crawlState = await spiderClient.query({ domain: "spider.cloud" });

    assert(typeof crawlState === "object");
    assert(crawlState.content);
  });

  // unkown error (400 bad request)
  // test("should get credits", async () => {
  //   const spiderClient = new Spider();
  //   const credits = await spiderClient.getCredits();
  //   console.log("THIS IS THE GET CREDITS RESPONSE", credits)

  //   assert(typeof credits === 'object');
  // });

  test("should post data", async () => {
    const spiderClient = new Spider();
    const table = "websites";
    const postData = { url: url };
    const response = await spiderClient.postData(table, postData);
    assert(response.status == 201);
  });

  // 500 error code
  // test("should get data", async () => {
  //   const spiderClient = new Spider();
  //   const table = "websites";
  //   const response = await spiderClient.getData(table, params);

  //   assert(typeof response === 'object');
  //   assert(Array.isArray(response.data));
  // });

  test("should delete data", async () => {
    const spiderClient = new Spider();
    const table = "websites";
    const response = await spiderClient.deleteData(table, params);

    assert(response.status >= 200 && response.status <= 299);
  });

  // 500 error code
  // test("should create signed url", async () => {
  //   const spiderClient = new Spider();
  //   const signedUrl = await spiderClient.createSignedUrl("example.com", { page: 1, limit: 10 });
  //
  //   assert(typeof signedUrl === 'string');
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
