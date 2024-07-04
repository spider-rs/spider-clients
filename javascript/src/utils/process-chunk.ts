import type { SpiderCoreResponse } from "../config";

export const processChunk = (
  chunk: string,
  cb: (r: SpiderCoreResponse) => void
) => {
  try {
    cb(chunk ? JSON.parse(chunk.trim()) : null);

    return true;
  } catch (_error) {
    return false;
  }
};
