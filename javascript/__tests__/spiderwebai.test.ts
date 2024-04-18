import SpiderWebAIApp from "../src/spiderwebai";

describe("SpiderWebAIApp", () => {
  it("should throw error if API key is not provided", () => {
    expect(() => new SpiderWebAIApp()).toThrow("No API key provided");
  });
});
