package main

import (
	"context"
	"fmt"
	"log"

	spider "github.com/spider-rs/spider-clients/go"
)

func main() {
	client := spider.New("") // Uses SPIDER_API_KEY env var

	fmt.Println("Crawling https://example.com (limit: 5 pages)...")

	pages, err := client.CrawlURL(context.Background(), "https://example.com", &spider.SpiderParams{
		Limit:        5,
		ReturnFormat: spider.FormatMarkdown,
		Request:      spider.RequestSmart,
	})
	if err != nil {
		log.Fatalf("Crawl failed: %v", err)
	}

	fmt.Printf("\nCrawled %d pages:\n\n", len(pages))
	for _, page := range pages {
		content := page.Content
		if len(content) > 200 {
			content = content[:200] + "..."
		}
		fmt.Printf("URL: %s\nContent preview: %s\n\n", page.URL, content)
	}
}
