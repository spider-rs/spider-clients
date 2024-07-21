import type { ChunkCallbackFunction } from "../config";
import { processChunk } from "./process-chunk";

// stream the response via callbacks.
export const streamReader = async (
  res: Response,
  cb: ChunkCallbackFunction,
) => {
  if (res.ok) {
    const reader = res.body?.getReader();
    const decoder = new TextDecoder();

    if (reader) {
      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        const chunk = decoder.decode(value, { stream: true });

        processChunk(chunk, cb);
      }
    }
  }
};
