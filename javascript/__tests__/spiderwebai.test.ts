import Spider from "../src/spiderwebai";

describe("Spider", () => {
  it("should throw error if API key is not provided", () => {
    expect(() => new Spider()).toThrow("No API key provided");
  });
});
