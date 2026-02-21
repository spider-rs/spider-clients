package main

import (
	"context"
	"fmt"
	"log"

	spider "github.com/spider-rs/spider-clients/go"
)

func main() {
	client := spider.New("") // Uses SPIDER_API_KEY env var
	client.SetAIStudioTier(spider.TierStandard)

	fmt.Println("AI Scraping https://example.com...")

	result, err := client.AIScrape(
		context.Background(),
		"https://example.com",
		"Extract the main heading and page description",
		nil,
	)
	if err != nil {
		switch e := err.(type) {
		case *spider.AIStudioSubscriptionRequired:
			log.Fatalf("AI Studio subscription required: %v", e)
		case *spider.AIStudioRateLimitExceeded:
			log.Fatalf("Rate limited, retry after %dms: %v", e.RetryAfterMs, e)
		default:
			log.Fatalf("AI Scrape failed: %v", err)
		}
	}

	fmt.Printf("Result:\n%s\n", string(result))
}
