package spider

import (
	"bufio"
	"encoding/json"
	"io"
)

// StreamCallback is invoked for each SpiderResponse received during
// a JSONL streaming response.
type StreamCallback func(SpiderResponse)

// streamJSONL reads JSONL (newline-delimited JSON) from r and calls cb
// for each successfully parsed SpiderResponse. It returns on EOF or
// on the first read error.
func streamJSONL(r io.Reader, cb StreamCallback) error {
	scanner := bufio.NewScanner(r)

	// Allow up to 10 MB per line (pages can be large).
	scanner.Buffer(make([]byte, 0, 64*1024), 10*1024*1024)

	for scanner.Scan() {
		line := scanner.Bytes()
		if len(line) == 0 {
			continue
		}
		var resp SpiderResponse
		if err := json.Unmarshal(line, &resp); err != nil {
			// Skip malformed lines rather than aborting.
			continue
		}
		cb(resp)
	}
	return scanner.Err()
}
