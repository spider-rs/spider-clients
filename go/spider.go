// Package spider provides a Go client for the Spider web crawling API.
//
// The client supports all Spider API endpoints including crawling, scraping,
// search, screenshots, transform, unblocker, and AI Studio features.
//
// Basic usage:
//
//	client := spider.New("") // uses SPIDER_API_KEY env var
//	pages, err := client.CrawlURL(ctx, "https://example.com", &spider.SpiderParams{
//	    Limit:        10,
//	    ReturnFormat: spider.FormatMarkdown,
//	})
package spider

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"math"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"
)

// Option configures the Spider client.
type Option func(*Spider)

// WithHTTPClient sets a custom http.Client.
func WithHTTPClient(c *http.Client) Option {
	return func(s *Spider) { s.httpClient = c }
}

// WithBaseURL overrides the default API base URL.
func WithBaseURL(url string) Option {
	return func(s *Spider) { s.baseURL = url }
}

// WithAIStudioTier sets the AI Studio subscription tier for rate limiting.
func WithAIStudioTier(tier AIStudioTier) Option {
	return func(s *Spider) {
		s.aiTier = tier
		if limit, ok := AIStudioRateLimits[tier]; ok {
			s.rateLimiter.setLimit(limit)
		}
	}
}

// RateLimitInfo holds the latest rate limit state from API response headers.
type RateLimitInfo struct {
	// Maximum requests allowed per minute.
	Limit int
	// Requests remaining in the current window.
	Remaining int
	// Seconds until the rate limit window resets.
	ResetSeconds int
}

// Spider is the API client.
type Spider struct {
	apiKey      string
	baseURL     string
	httpClient  *http.Client
	aiTier      AIStudioTier
	rateLimiter *rateLimiter

	// RateLimit holds the latest rate limit info from API responses.
	RateLimit RateLimitInfo
}

// New creates a new Spider client. If apiKey is empty, the SPIDER_API_KEY
// environment variable is used. Panics if no key is found.
func New(apiKey string, opts ...Option) *Spider {
	if apiKey == "" {
		apiKey = os.Getenv("SPIDER_API_KEY")
	}
	if apiKey == "" {
		panic("spider: no API key provided (set SPIDER_API_KEY or pass to New)")
	}

	s := &Spider{
		apiKey:  apiKey,
		baseURL: BaseURL,
		httpClient: &http.Client{
			Timeout: 5 * time.Minute,
		},
		aiTier:      TierStarter,
		rateLimiter: newRateLimiter(AIStudioRateLimits[TierStarter]),
	}
	for _, opt := range opts {
		opt(s)
	}
	return s
}

// SetBaseURL changes the API base URL.
func (s *Spider) SetBaseURL(url string) { s.baseURL = url }

// SetAIStudioTier updates the AI Studio tier and adjusts rate limiting.
func (s *Spider) SetAIStudioTier(tier AIStudioTier) {
	s.aiTier = tier
	if limit, ok := AIStudioRateLimits[tier]; ok {
		s.rateLimiter.setLimit(limit)
	}
}

// ---------- Core endpoints ----------

// CrawlURL crawls a website starting from url.
func (s *Spider) CrawlURL(ctx context.Context, url string, params *SpiderParams) ([]SpiderResponse, error) {
	body := s.mergeURL(url, params)
	return s.apiPost(ctx, RouteCrawl, body)
}

// CrawlURLStream is like CrawlURL but streams results via JSONL,
// invoking cb for each page as it arrives.
func (s *Spider) CrawlURLStream(ctx context.Context, url string, params *SpiderParams, cb StreamCallback) error {
	body := s.mergeURL(url, params)
	return s.apiPostStream(ctx, RouteCrawl, body, cb)
}

// ScrapeURL scrapes a single page (crawl with limit=1).
func (s *Spider) ScrapeURL(ctx context.Context, url string, params *SpiderParams) ([]SpiderResponse, error) {
	body := s.mergeURL(url, params)
	body["limit"] = 1
	return s.apiPost(ctx, RouteCrawl, body)
}

// Links retrieves all links from url.
func (s *Spider) Links(ctx context.Context, url string, params *SpiderParams) ([]SpiderResponse, error) {
	body := s.mergeURL(url, params)
	return s.apiPost(ctx, RouteLinks, body)
}

// Screenshot takes a screenshot of url.
func (s *Spider) Screenshot(ctx context.Context, url string, params *SpiderParams) ([]SpiderResponse, error) {
	body := s.mergeURL(url, params)
	return s.apiPost(ctx, RouteScreenshot, body)
}

// Search performs a web search and optionally crawls results.
func (s *Spider) Search(ctx context.Context, query string, params *SearchParams) ([]SpiderResponse, error) {
	body := structToMap(params)
	body["search"] = query
	return s.apiPost(ctx, RouteSearch, body)
}

// Transform converts HTML to markdown/text.
func (s *Spider) Transform(ctx context.Context, params *TransformParams) ([]SpiderResponse, error) {
	body := structToMap(params)
	return s.apiPost(ctx, RouteTransform, body)
}

// Unblocker fetches a URL through anti-bot bypass.
func (s *Spider) Unblocker(ctx context.Context, url string, params *SpiderParams) ([]SpiderResponse, error) {
	body := s.mergeURL(url, params)
	return s.apiPost(ctx, RouteUnblocker, body)
}

// GetCredits returns the account credit balance.
func (s *Spider) GetCredits(ctx context.Context) (*Credits, error) {
	data, err := s.apiGet(ctx, RouteDataCredits)
	if err != nil {
		return nil, err
	}
	var c Credits
	if err := json.Unmarshal(data, &c); err != nil {
		return nil, fmt.Errorf("spider: decode credits: %w", err)
	}
	return &c, nil
}

// PostData inserts data into a collection.
func (s *Spider) PostData(ctx context.Context, collection Collection, data map[string]interface{}) (json.RawMessage, error) {
	endpoint := RouteData + "/" + string(collection)
	raw, err := s.doPost(ctx, endpoint, data, false)
	if err != nil {
		return nil, err
	}
	defer raw.Body.Close()
	return io.ReadAll(raw.Body)
}

// ---------- AI Studio endpoints ----------

// AICrawl performs AI-guided crawling.
func (s *Spider) AICrawl(ctx context.Context, url, prompt string, params *AIParams) (json.RawMessage, error) {
	body := s.mergeAI(url, prompt, params)
	return s.aiPost(ctx, RouteAICrawl, body)
}

// AIScrape performs AI-guided single-page extraction.
func (s *Spider) AIScrape(ctx context.Context, url, prompt string, params *AIParams) (json.RawMessage, error) {
	body := s.mergeAI(url, prompt, params)
	return s.aiPost(ctx, RouteAIScrape, body)
}

// AISearch performs AI-enhanced web search.
func (s *Spider) AISearch(ctx context.Context, prompt string, params *SearchParams) (json.RawMessage, error) {
	body := structToMap(params)
	body["prompt"] = prompt
	return s.aiPost(ctx, RouteAISearch, body)
}

// AIBrowser performs AI-guided browser automation.
func (s *Spider) AIBrowser(ctx context.Context, url, prompt string, params *AIParams) (json.RawMessage, error) {
	body := s.mergeAI(url, prompt, params)
	return s.aiPost(ctx, RouteAIBrowser, body)
}

// AILinks performs AI-guided link extraction.
func (s *Spider) AILinks(ctx context.Context, url, prompt string, params *AIParams) (json.RawMessage, error) {
	body := s.mergeAI(url, prompt, params)
	return s.aiPost(ctx, RouteAILinks, body)
}

// ---------- Internal HTTP helpers ----------

func (s *Spider) endpoint(route string) string {
	return s.baseURL + "/" + APIVersion + "/" + route
}

func (s *Spider) headers(contentType string) http.Header {
	h := http.Header{}
	h.Set("Content-Type", contentType)
	h.Set("Authorization", "Bearer "+s.apiKey)
	h.Set("User-Agent", "Spider-Client/"+Version)
	return h
}

func (s *Spider) updateRateLimit(header http.Header) {
	if v := header.Get("RateLimit-Limit"); v != "" {
		if n, err := strconv.Atoi(v); err == nil {
			s.RateLimit.Limit = n
		}
	}
	if v := header.Get("RateLimit-Remaining"); v != "" {
		if n, err := strconv.Atoi(v); err == nil {
			s.RateLimit.Remaining = n
		}
	}
	if v := header.Get("RateLimit-Reset"); v != "" {
		if n, err := strconv.Atoi(v); err == nil {
			s.RateLimit.ResetSeconds = n
		}
	}
}

// doPost sends a POST with retries and returns the raw response.
// The caller must close resp.Body.
func (s *Spider) doPost(ctx context.Context, route string, body interface{}, jsonl bool) (*http.Response, error) {
	payload, err := json.Marshal(body)
	if err != nil {
		return nil, fmt.Errorf("spider: marshal body: %w", err)
	}

	ct := "application/json"
	if jsonl {
		ct = "application/jsonl"
	}

	var resp *http.Response
	for attempt := 0; attempt < 5; attempt++ {
		if attempt > 0 {
			backoff := time.Duration(math.Pow(2, float64(attempt-1))) * time.Second
			if backoff > 60*time.Second {
				backoff = 60 * time.Second
			}
			select {
			case <-ctx.Done():
				return nil, ctx.Err()
			case <-time.After(backoff):
			}
		}

		req, err := http.NewRequestWithContext(ctx, "POST", s.endpoint(route), bytes.NewReader(payload))
		if err != nil {
			return nil, fmt.Errorf("spider: create request: %w", err)
		}
		req.Header = s.headers(ct)

		resp, err = s.httpClient.Do(req)
		if err != nil {
			continue // retry on network error
		}

		s.updateRateLimit(resp.Header)

		if resp.StatusCode == http.StatusTooManyRequests {
			retryAfter := 1
			if ra := resp.Header.Get("Retry-After"); ra != "" {
				if secs, err := strconv.Atoi(ra); err == nil {
					retryAfter = secs
				}
			}
			resp.Body.Close()
			select {
			case <-ctx.Done():
				return nil, ctx.Err()
			case <-time.After(time.Duration(retryAfter) * time.Second):
			}
			continue
		}

		if resp.StatusCode >= 500 {
			resp.Body.Close()
			continue // retry on server error
		}
		return resp, nil
	}
	if resp != nil {
		return resp, nil
	}
	return nil, fmt.Errorf("spider: POST %s failed after 5 attempts", route)
}

func (s *Spider) apiPost(ctx context.Context, route string, body interface{}) ([]SpiderResponse, error) {
	resp, err := s.doPost(ctx, route, body, false)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, &APIError{StatusCode: resp.StatusCode, Action: "POST " + route}
	}

	var results []SpiderResponse
	if err := json.NewDecoder(resp.Body).Decode(&results); err != nil {
		return nil, fmt.Errorf("spider: decode response: %w", err)
	}
	return results, nil
}

func (s *Spider) apiPostStream(ctx context.Context, route string, body interface{}, cb StreamCallback) error {
	resp, err := s.doPost(ctx, route, body, true)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return &APIError{StatusCode: resp.StatusCode, Action: "POST stream " + route}
	}

	return streamJSONL(resp.Body, cb)
}

func (s *Spider) apiGet(ctx context.Context, route string) (json.RawMessage, error) {
	var resp *http.Response
	var err error

	for attempt := 0; attempt < 5; attempt++ {
		if attempt > 0 {
			backoff := time.Duration(math.Pow(2, float64(attempt-1))) * time.Second
			if backoff > 60*time.Second {
				backoff = 60 * time.Second
			}
			select {
			case <-ctx.Done():
				return nil, ctx.Err()
			case <-time.After(backoff):
			}
		}

		req, reqErr := http.NewRequestWithContext(ctx, "GET", s.endpoint(route), nil)
		if reqErr != nil {
			return nil, fmt.Errorf("spider: create request: %w", reqErr)
		}
		req.Header = s.headers("application/json")

		resp, err = s.httpClient.Do(req)
		if err != nil {
			continue
		}

		s.updateRateLimit(resp.Header)

		if resp.StatusCode == http.StatusTooManyRequests {
			retryAfter := 1
			if ra := resp.Header.Get("Retry-After"); ra != "" {
				if secs, parseErr := strconv.Atoi(ra); parseErr == nil {
					retryAfter = secs
				}
			}
			resp.Body.Close()
			select {
			case <-ctx.Done():
				return nil, ctx.Err()
			case <-time.After(time.Duration(retryAfter) * time.Second):
			}
			continue
		}

		if resp.StatusCode >= 500 {
			resp.Body.Close()
			continue
		}
		break
	}
	if resp == nil {
		if err != nil {
			return nil, err
		}
		return nil, fmt.Errorf("spider: GET %s failed after 5 attempts", route)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, &APIError{StatusCode: resp.StatusCode, Action: "GET " + route}
	}

	return io.ReadAll(resp.Body)
}

func (s *Spider) aiPost(ctx context.Context, route string, body interface{}) (json.RawMessage, error) {
	s.rateLimiter.acquire()

	resp, err := s.doPost(ctx, route, body, false)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	switch resp.StatusCode {
	case http.StatusOK:
		return io.ReadAll(resp.Body)
	case http.StatusPaymentRequired:
		return nil, &AIStudioSubscriptionRequired{}
	case http.StatusTooManyRequests:
		retryAfter := 1000
		if ra := resp.Header.Get("Retry-After"); ra != "" {
			if secs, err := strconv.Atoi(ra); err == nil {
				retryAfter = secs * 1000
			}
		}
		return nil, &AIStudioRateLimitExceeded{RetryAfterMs: retryAfter}
	default:
		return nil, &APIError{StatusCode: resp.StatusCode, Action: "AI POST " + route}
	}
}

// ---------- Parameter helpers ----------

func (s *Spider) mergeURL(url string, params *SpiderParams) map[string]interface{} {
	m := structToMap(params)
	m["url"] = url
	return m
}

func (s *Spider) mergeAI(url, prompt string, params *AIParams) map[string]interface{} {
	m := structToMap(params)
	m["url"] = url
	m["prompt"] = prompt
	return m
}

// structToMap converts a struct to map[string]interface{} via JSON round-trip,
// omitting zero-value fields (due to omitempty tags). Returns an empty map
// if v is nil or marshals to JSON null.
func structToMap(v interface{}) map[string]interface{} {
	if v == nil {
		return map[string]interface{}{}
	}
	data, err := json.Marshal(v)
	if err != nil || string(data) == "null" {
		return map[string]interface{}{}
	}
	m := map[string]interface{}{}
	json.Unmarshal(data, &m)
	return m
}

// ---------- Rate limiter ----------

type rateLimiter struct {
	mu         sync.Mutex
	timestamps []int64
	maxReqs    int
	windowMs   int64
}

func newRateLimiter(requestsPerSecond int) *rateLimiter {
	return &rateLimiter{
		maxReqs:  requestsPerSecond,
		windowMs: 1000,
	}
}

func (rl *rateLimiter) setLimit(requestsPerSecond int) {
	rl.mu.Lock()
	defer rl.mu.Unlock()
	rl.maxReqs = requestsPerSecond
}

func (rl *rateLimiter) acquire() {
	for {
		waitMs := rl.tryAcquire()
		if waitMs == 0 {
			return
		}
		time.Sleep(time.Duration(waitMs) * time.Millisecond)
	}
}

func (rl *rateLimiter) tryAcquire() int64 {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	now := time.Now().UnixMilli()

	// Remove timestamps outside the window.
	fresh := rl.timestamps[:0]
	for _, ts := range rl.timestamps {
		if now-ts < rl.windowMs {
			fresh = append(fresh, ts)
		}
	}
	rl.timestamps = fresh

	if len(rl.timestamps) >= rl.maxReqs {
		oldest := rl.timestamps[0]
		wait := rl.windowMs - (now - oldest)
		if wait < 1 {
			wait = 1
		}
		return wait
	}

	rl.timestamps = append(rl.timestamps, now)
	return 0
}
