import type { SpiderCoreResponse } from "../config";

export const createJsonLineProcessor = (
  cb: (r: SpiderCoreResponse) => void
) => {
  let buffer = "";

  return (chunk: Buffer | string) => {
    buffer += chunk.toString();
    let boundary: number;

    while ((boundary = buffer.indexOf("\n")) !== -1) {
      const line = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 1);

      if (line.trim()) {
        try {
          cb(JSON.parse(line));
        } catch (_error) {}
      }
    }
  };
};
