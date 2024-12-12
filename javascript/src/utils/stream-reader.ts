import type { ChunkCallbackFunction } from "../config";
import { createJsonLineProcessor } from "./process-chunk";

// Stream the response via callbacks.
export const streamReader = async (
  res: Response,
  cb: ChunkCallbackFunction
) => {
  if (res.ok) {
    const reader = res.body?.getReader();
    const decoder = new TextDecoder();
    const processChunk = createJsonLineProcessor(cb);

    if (reader) {
      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        processChunk(chunk);
      }

      processChunk(decoder.decode(new Uint8Array(), { stream: false }));
    }
  }
};
