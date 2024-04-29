import { describe, test, expect, jest } from '@jest/globals';
import Spider from "../src/spiderwebai";

describe("Spider JS SDK", () => {
  test("should throw error if API key is not provided", () => {
    expect(() => new Spider({ apiKey: undefined })).toThrow("No API key provided");
  });
});
