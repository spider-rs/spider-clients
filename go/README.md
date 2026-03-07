# Spider Go SDK

Official Go client for the [Spider](https://spider.cloud) web crawling API.

## Installation

```bash
go get github.com/spider-rs/spider-clients/go
```

## Quick Start

```go
package main

import (
    "context"
    "fmt"
    "log"

    spider "github.com/spider-rs/spider-clients/go"
)

func main() {
    // Uses SPIDER_API_KEY env var by default
    client := spider.New("")

    pages, err := client.CrawlURL(context.Background(), "https://example.com", &spider.SpiderParams{
        Limit:        10,
        ReturnFormat: spider.FormatMarkdown,
    })
    if err != nil {
        log.Fatal(err)
    }

    for _, page := range pages {
        fmt.Printf("%s: %d chars\n", page.URL, len(page.Content))
    }
}
```

## Configuration

```go
// Explicit API key
client := spider.New("sk-your-api-key")

// Custom HTTP client
client := spider.New("", spider.WithHTTPClient(&http.Client{
    Timeout: 10 * time.Minute,
}))

// Custom base URL
client := spider.New("", spider.WithBaseURL("https://custom-api.example.com"))

// AI Studio tier for rate limiting
client := spider.New("", spider.WithAIStudioTier(spider.TierStandard))
```

## Endpoints

### Crawl

```go
pages, err := client.CrawlURL(ctx, "https://example.com", &spider.SpiderParams{
    Limit:        50,
    ReturnFormat: spider.FormatMarkdown,
    Request:      spider.RequestSmart,
})
```

### Crawl with streaming

```go
err := client.CrawlURLStream(ctx, "https://example.com", &spider.SpiderParams{
    Limit:        100,
    ReturnFormat: spider.FormatMarkdown,
}, func(page spider.SpiderResponse) {
    fmt.Printf("Received: %s\n", page.URL)
})
```

### Scrape (single page)

```go
pages, err := client.ScrapeURL(ctx, "https://example.com/page", &spider.SpiderParams{
    ReturnFormat: spider.FormatMarkdown,
})
```

### Search

```go
pages, err := client.Search(ctx, "web scraping APIs", &spider.SearchParams{
    SearchLimit: 5,
    SpiderParams: spider.SpiderParams{
        ReturnFormat: spider.FormatMarkdown,
    },
})
```

### Screenshot

```go
pages, err := client.Screenshot(ctx, "https://example.com", nil)
```

### Links

```go
pages, err := client.Links(ctx, "https://example.com", nil)
```

### Transform

```go
pages, err := client.Transform(ctx, &spider.TransformParams{
    Data: []spider.Resource{
        {HTML: "<h1>Hello</h1><p>World</p>", URL: "https://example.com"},
    },
    ReturnFormat: spider.FormatMarkdown,
})
```

### Credits

```go
credits, err := client.GetCredits(ctx)
fmt.Printf("Credits: %d\n", credits.Credits)
```

## AI Studio

AI Studio endpoints require an active subscription.

```go
// Set tier for client-side rate limiting
client.SetAIStudioTier(spider.TierStandard)

// AI Crawl
result, err := client.AICrawl(ctx, "https://example.com", "Extract all product names and prices", nil)

// AI Scrape
result, err := client.AIScrape(ctx, "https://example.com/pricing", "Get all plan names and monthly costs", nil)

// AI Search
result, err := client.AISearch(ctx, "Find the top 5 web scraping APIs with pricing", nil)

// AI Browser
result, err := client.AIBrowser(ctx, "https://example.com", "Click the login button and fill in the form", nil)

// AI Links
result, err := client.AILinks(ctx, "https://example.com", "Find all documentation links", nil)
```

## Error Handling

```go
pages, err := client.AICrawl(ctx, url, prompt, nil)
if err != nil {
    switch e := err.(type) {
    case *spider.AIStudioSubscriptionRequired:
        // Need to subscribe at https://spider.cloud/ai-studio
    case *spider.AIStudioRateLimitExceeded:
        // Wait e.RetryAfterMs milliseconds before retrying
    case *spider.APIError:
        // HTTP error: e.StatusCode
    default:
        // Network or other error
    }
}
```

## Browser Automation

The Go client integrates with the [spider-browser](https://github.com/spider-rs/spider-browser/tree/main/go) SDK for WebSocket-based browser automation with CDP/BiDi support.

```go
client := spider.New("your-api-key")

// Create a browser instance (inherits API key from client)
browser := client.Browser(
    spider.WithBrowserType("chrome"),
    spider.WithLLM(spider.LLMConfig{
        Provider: "openai",
        Model:    "gpt-4o",
        APIKey:   "your-openai-key",
    }),
)

if err := browser.Init(); err != nil {
    log.Fatal(err)
}
defer browser.Close()

// Navigate
if err := browser.Goto("https://example.com"); err != nil {
    log.Fatal(err)
}

// AI-powered actions
browser.Act("Click the login button")

// Get page content
html, _ := browser.Page().Content(8000, 1000)
```

## License

MIT
