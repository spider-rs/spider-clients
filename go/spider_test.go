package spider

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"
)

func TestNewWithAPIKey(t *testing.T) {
	s := New("test-key-123")
	if s.apiKey != "test-key-123" {
		t.Errorf("expected apiKey 'test-key-123', got '%s'", s.apiKey)
	}
	if s.baseURL != BaseURL {
		t.Errorf("expected baseURL '%s', got '%s'", BaseURL, s.baseURL)
	}
}

func TestNewFromEnv(t *testing.T) {
	os.Setenv("SPIDER_API_KEY", "env-key-456")
	defer os.Unsetenv("SPIDER_API_KEY")

	s := New("")
	if s.apiKey != "env-key-456" {
		t.Errorf("expected apiKey 'env-key-456', got '%s'", s.apiKey)
	}
}

func TestNewPanicsWithoutKey(t *testing.T) {
	os.Unsetenv("SPIDER_API_KEY")
	defer func() {
		if r := recover(); r == nil {
			t.Error("expected panic when no API key provided")
		}
	}()
	New("")
}

func TestSetBaseURL(t *testing.T) {
	s := New("key")
	s.SetBaseURL("https://custom.api.com")
	if s.baseURL != "https://custom.api.com" {
		t.Errorf("expected custom base URL, got '%s'", s.baseURL)
	}
}

func TestSetAIStudioTier(t *testing.T) {
	s := New("key")
	s.SetAIStudioTier(TierStandard)
	if s.aiTier != TierStandard {
		t.Errorf("expected tier 'standard', got '%s'", s.aiTier)
	}
}

func TestEndpointConstruction(t *testing.T) {
	s := New("key")
	got := s.endpoint(RouteCrawl)
	want := BaseURL + "/v1/crawl"
	if got != want {
		t.Errorf("endpoint() = %q, want %q", got, want)
	}
}

func TestStructToMapOmitsEmpty(t *testing.T) {
	p := &SpiderParams{
		Limit:        5,
		ReturnFormat: FormatMarkdown,
	}
	m := structToMap(p)

	if m["limit"] != float64(5) {
		t.Errorf("expected limit=5, got %v", m["limit"])
	}
	if m["return_format"] != "markdown" {
		t.Errorf("expected return_format=markdown, got %v", m["return_format"])
	}
	// Zero-value fields should be omitted.
	if _, ok := m["depth"]; ok {
		t.Error("expected depth to be omitted")
	}
	if _, ok := m["stealth"]; ok {
		t.Error("expected stealth to be omitted")
	}
}

func TestStructToMapNil(t *testing.T) {
	m := structToMap(nil)
	if len(m) != 0 {
		t.Errorf("expected empty map for nil, got %d entries", len(m))
	}
}

func TestCrawlURL(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" {
			t.Errorf("expected POST, got %s", r.Method)
		}
		if !strings.HasSuffix(r.URL.Path, "/v1/crawl") {
			t.Errorf("expected /v1/crawl, got %s", r.URL.Path)
		}
		if r.Header.Get("Authorization") != "Bearer test-key" {
			t.Errorf("expected Bearer auth, got %s", r.Header.Get("Authorization"))
		}
		if r.Header.Get("User-Agent") != "Spider-Client/"+Version {
			t.Errorf("expected user agent, got %s", r.Header.Get("User-Agent"))
		}

		var body map[string]interface{}
		json.NewDecoder(r.Body).Decode(&body)
		if body["url"] != "https://example.com" {
			t.Errorf("expected url in body, got %v", body["url"])
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode([]SpiderResponse{
			{URL: "https://example.com", Content: "# Hello", Status: 200},
		})
	}))
	defer server.Close()

	s := New("test-key", WithBaseURL(server.URL))
	pages, err := s.CrawlURL(context.Background(), "https://example.com", &SpiderParams{
		Limit:        5,
		ReturnFormat: FormatMarkdown,
	})
	if err != nil {
		t.Fatalf("CrawlURL error: %v", err)
	}
	if len(pages) != 1 {
		t.Fatalf("expected 1 page, got %d", len(pages))
	}
	if pages[0].URL != "https://example.com" {
		t.Errorf("expected url, got %s", pages[0].URL)
	}
	if pages[0].Content != "# Hello" {
		t.Errorf("expected content, got %s", pages[0].Content)
	}
}

func TestScrapeURLSetsLimit1(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var body map[string]interface{}
		json.NewDecoder(r.Body).Decode(&body)
		if body["limit"] != float64(1) {
			t.Errorf("ScrapeURL should set limit=1, got %v", body["limit"])
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode([]SpiderResponse{{URL: "https://example.com"}})
	}))
	defer server.Close()

	s := New("test-key", WithBaseURL(server.URL))
	_, err := s.ScrapeURL(context.Background(), "https://example.com", nil)
	if err != nil {
		t.Fatalf("ScrapeURL error: %v", err)
	}
}

func TestCrawlURLStream(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("Content-Type") != "application/jsonl" {
			t.Errorf("expected jsonl content type, got %s", r.Header.Get("Content-Type"))
		}
		w.Header().Set("Content-Type", "application/jsonl")
		// Write two JSONL lines.
		w.Write([]byte(`{"url":"https://example.com/1","content":"page1"}` + "\n"))
		w.Write([]byte(`{"url":"https://example.com/2","content":"page2"}` + "\n"))
	}))
	defer server.Close()

	s := New("test-key", WithBaseURL(server.URL))
	var pages []SpiderResponse
	err := s.CrawlURLStream(context.Background(), "https://example.com", nil, func(resp SpiderResponse) {
		pages = append(pages, resp)
	})
	if err != nil {
		t.Fatalf("CrawlURLStream error: %v", err)
	}
	if len(pages) != 2 {
		t.Fatalf("expected 2 streamed pages, got %d", len(pages))
	}
}

func TestGetCredits(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "GET" {
			t.Errorf("expected GET, got %s", r.Method)
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(Credits{Credits: 5000})
	}))
	defer server.Close()

	s := New("test-key", WithBaseURL(server.URL))
	credits, err := s.GetCredits(context.Background())
	if err != nil {
		t.Fatalf("GetCredits error: %v", err)
	}
	if credits.Credits != 5000 {
		t.Errorf("expected 5000 credits, got %d", credits.Credits)
	}
}

func TestAPIError(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusForbidden)
	}))
	defer server.Close()

	s := New("test-key", WithBaseURL(server.URL))
	_, err := s.CrawlURL(context.Background(), "https://example.com", nil)
	if err == nil {
		t.Fatal("expected error for 403 response")
	}
	apiErr, ok := err.(*APIError)
	if !ok {
		t.Fatalf("expected APIError, got %T: %v", err, err)
	}
	if apiErr.StatusCode != 403 {
		t.Errorf("expected status 403, got %d", apiErr.StatusCode)
	}
}

func TestRateLimiter(t *testing.T) {
	rl := newRateLimiter(2)

	// First two acquisitions should be immediate.
	wait1 := rl.tryAcquire()
	wait2 := rl.tryAcquire()
	if wait1 != 0 || wait2 != 0 {
		t.Errorf("first two should be immediate, got wait1=%d wait2=%d", wait1, wait2)
	}

	// Third should require waiting.
	wait3 := rl.tryAcquire()
	if wait3 == 0 {
		t.Error("third acquisition should require waiting")
	}
}

func TestAIStudio402(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusPaymentRequired)
	}))
	defer server.Close()

	s := New("test-key", WithBaseURL(server.URL))
	_, err := s.AICrawl(context.Background(), "https://example.com", "test prompt", nil)
	if err == nil {
		t.Fatal("expected error for 402 response")
	}
	if _, ok := err.(*AIStudioSubscriptionRequired); !ok {
		t.Fatalf("expected AIStudioSubscriptionRequired, got %T: %v", err, err)
	}
}

func TestAIStudio429(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Retry-After", "5")
		w.WriteHeader(http.StatusTooManyRequests)
	}))
	defer server.Close()

	s := New("test-key", WithBaseURL(server.URL))
	_, err := s.AICrawl(context.Background(), "https://example.com", "test prompt", nil)
	if err == nil {
		t.Fatal("expected error for 429 response")
	}
	rateErr, ok := err.(*AIStudioRateLimitExceeded)
	if !ok {
		t.Fatalf("expected AIStudioRateLimitExceeded, got %T: %v", err, err)
	}
	if rateErr.RetryAfterMs != 5000 {
		t.Errorf("expected RetryAfterMs=5000, got %d", rateErr.RetryAfterMs)
	}
}
