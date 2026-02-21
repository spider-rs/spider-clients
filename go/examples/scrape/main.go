package main

import (
	"context"
	"fmt"
	"log"

	spider "github.com/spider-rs/spider-clients/go"
)

func main() {
	client := spider.New("") // Uses SPIDER_API_KEY env var

	fmt.Println("Scraping https://example.com...")

	pages, err := client.ScrapeURL(context.Background(), "https://example.com", &spider.SpiderParams{
		ReturnFormat: spider.FormatMarkdown,
	})
	if err != nil {
		log.Fatalf("Scrape failed: %v", err)
	}

	if len(pages) > 0 {
		fmt.Printf("URL: %s\n", pages[0].URL)
		fmt.Printf("Content:\n%s\n", pages[0].Content)
	}
}
