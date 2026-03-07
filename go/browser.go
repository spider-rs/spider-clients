package spider

import (
	spiderbrowser "github.com/spider-rs/spider-browser/go"
)

// Re-export spider-browser types for convenience.
type (
	// SpiderBrowser provides WebSocket-based browser automation (CDP/BiDi).
	SpiderBrowser = spiderbrowser.SpiderBrowser

	// SpiderBrowserOptions configures a SpiderBrowser instance.
	SpiderBrowserOptions = spiderbrowser.SpiderBrowserOptions

	// SpiderPage provides page interaction methods (click, fill, screenshot, etc.).
	SpiderPage = spiderbrowser.SpiderPage

	// LLMConfig configures the LLM provider for AI-powered browser actions.
	LLMConfig = spiderbrowser.LLMConfig

	// Agent is an autonomous multi-step browser automation agent.
	Agent = spiderbrowser.Agent

	// AgentOptions configures the Agent.
	AgentOptions = spiderbrowser.AgentOptions

	// AgentResult is the result of an Agent execution.
	AgentResult = spiderbrowser.AgentResult

	// ObserveResult represents an observed interactive element on the page.
	ObserveResult = spiderbrowser.ObserveResult
)

// BrowserOption configures a SpiderBrowser created via Spider.Browser().
type BrowserOption func(*SpiderBrowserOptions)

// WithBrowserType sets the browser type (e.g. "chrome", "firefox", "auto").
func WithBrowserType(browser string) BrowserOption {
	return func(o *SpiderBrowserOptions) { o.Browser = browser }
}

// WithServerURL overrides the default WebSocket server URL.
func WithServerURL(url string) BrowserOption {
	return func(o *SpiderBrowserOptions) { o.ServerURL = url }
}

// WithStealth sets the initial stealth level (0-3, 0=auto-escalate).
func WithStealth(level int) BrowserOption {
	return func(o *SpiderBrowserOptions) { o.Stealth = level }
}

// WithLLM sets the LLM configuration for AI-powered actions.
func WithLLM(config LLMConfig) BrowserOption {
	return func(o *SpiderBrowserOptions) { o.LLM = &config }
}

// WithCaptcha sets the captcha handling mode ("off", "detect", "solve").
func WithCaptcha(mode string) BrowserOption {
	return func(o *SpiderBrowserOptions) { o.Captcha = mode }
}

// WithCountry sets the country code for geo-located proxies.
func WithCountry(country string) BrowserOption {
	return func(o *SpiderBrowserOptions) { o.Country = country }
}

// WithProxyURL sets a custom proxy URL.
func WithProxyURL(proxyURL string) BrowserOption {
	return func(o *SpiderBrowserOptions) { o.ProxyURL = proxyURL }
}

// WithRecord enables screencast recording.
func WithRecord(record bool) BrowserOption {
	return func(o *SpiderBrowserOptions) { o.Record = record }
}

// WithMode sets the browser mode ("scraping" or "cua").
func WithMode(mode string) BrowserOption {
	return func(o *SpiderBrowserOptions) { o.Mode = mode }
}

// Browser creates a new SpiderBrowser instance using this client's API key.
// The returned browser must be initialized with Init() before use.
//
//	client := spider.New("your-api-key")
//	browser := client.Browser(spider.WithBrowserType("chrome"), spider.WithLLM(spider.LLMConfig{...}))
//	if err := browser.Init(); err != nil { log.Fatal(err) }
//	defer browser.Close()
func (s *Spider) Browser(opts ...BrowserOption) *SpiderBrowser {
	options := SpiderBrowserOptions{
		APIKey: s.apiKey,
	}
	for _, opt := range opts {
		opt(&options)
	}
	return spiderbrowser.New(options)
}
