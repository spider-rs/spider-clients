# Spider Cloud Rust SDK

The Spider Cloud Rust SDK offers a toolkit for straightforward website scraping, crawling at scale, and other utilities like extracting links and taking screenshots, enabling you to collect data formatted for compatibility with language models (LLMs). It features a user-friendly interface for seamless integration with the Spider Cloud API.

## Installation

To use the Spider Cloud Rust SDK, include the following in your `Cargo.toml`:

```toml
[dependencies]
spider-client = "0.1"
```

## Usage

1. Get an API key from [spider.cloud](https://spider.cloud)
2. Set the API key as an environment variable named `SPIDER_API_KEY` or pass it as an argument when creating an instance of the `Spider` struct.

Here's an example of how to use the SDK:

```rust
use serde_json::json;
use std::env;

#[tokio::main]
async fn main() {
    // Set the API key as an environment variable
    env::set_var("SPIDER_API_KEY", "your_api_key");

    // Initialize the Spider with your API key
    let spider = Spider::new(None).expect("API key must be provided");

    let url = "https://spider.cloud";

    // Scrape a single URL
    let scraped_data = spider.scrape_url(url, None, false, "application/json").await.expect("Failed to scrape the URL");

    println!("Scraped Data: {:?}", scraped_data);

    // Crawl a website
    let crawler_params = RequestParams {
        limit: Some(1),
        proxy_enabled: Some(true),
        metadata: Some(false),
        request: Some(RequestType::Http),
        ..Default::default()
    };

    let crawl_result = spider.crawl_url(url, Some(crawler_params), false, "application/json", None::<fn(serde_json::Value)>).await.expect("Failed to crawl the URL");

    println!("Crawl Result: {:?}", crawl_result);
}
```

### Scraping a URL

To scrape data from a single URL:

```rust
let url = "https://example.com";
let scraped_data = spider.scrape_url(url, None, false, "application/json").await.expect("Failed to scrape the URL");
```

### Crawling a Website

To automate crawling a website:

```rust
let url = "https://example.com";
let crawl_params = RequestParams {
    limit: Some(200),
    request: Some(RequestType::Smart),
    ..Default::default()
};
let crawl_result = spider.crawl_url(url, Some(crawl_params), false, "application/json", None::<fn(serde_json::Value)>).await.expect("Failed to crawl the URL");
```

#### Crawl Streaming

Stream crawl the website in chunks to scale with a callback:

```rust
fn handle_json(json_obj: serde_json::Value) {
    println!("Received chunk: {:?}", json_obj);
}

let url = "https://example.com";
let crawl_params = RequestParams {
    limit: Some(200),
    ..Default::default()
};

spider.crawl_url(
    url,
    Some(crawl_params),
    true,
    "application/json",
    Some(handle_json)
).await.expect("Failed to crawl the URL");
```

### Search

Perform a search for websites to crawl or gather search results:

```rust
let query = "a sports website";
let crawl_params = RequestParams {
    request: Some(RequestType::Smart),
    search_limit: Some(5),
    limit: Some(5),
    fetch_page_content: Some(true),
    ..Default::default()
};
let crawl_result = spider.search(query, Some(crawl_params), false, "application/json").await.expect("Failed to perform search");
```

### Retrieving Links from a URL(s)

Extract all links from a specified URL:

```rust
let url = "https://example.com";
let links = spider.links(url, None, false, "application/json").await.expect("Failed to retrieve links from URL");
```

### Transform

Transform HTML to markdown or text lightning fast:

```rust
let data = vec![json!({"html": "<html><body><h1>Hello world</h1></body></html>"})];
let params = RequestParams {
    readability: Some(false),
    return_format: Some(ReturnFormat::Markdown),
    ..Default::default()
};
let result = spider.transform(data, Some(params), false, "application/json").await.expect("Failed to transform HTML to markdown");
println!("Transformed Data: {:?}", result);
```

### Taking Screenshots of a URL(s)

Capture a screenshot of a given URL:

```rust
let url = "https://example.com";
let screenshot = spider.screenshot(url, None, false, "application/json").await.expect("Failed to take screenshot of URL");
```

### Extracting Contact Information

Extract contact details from a specified URL:

```rust
let url = "https://example.com";
let contacts = spider.extract_contacts(url, None, false, "application/json").await.expect("Failed to extract contacts from URL");
println!("Extracted Contacts: {:?}", contacts);
```

### Checking Crawl State

You can check the crawl state of a specific URL:

```rust
let url = "https://example.com";
let state = spider.get_crawl_state(url, None, false, "application/json").await.expect("Failed to get crawl state for URL");
println!("Crawl State: {:?}", state);
```

### Downloading Files

You can download the results of the website:

```rust
let url = "https://example.com";
let options = hashmap!{
    "page" => 0,
    "limit" => 100,
    "expiresIn" => 3600 // Optional, add if needed
};
let response = spider.create_signed_url(Some(url), Some(options)).await.expect("Failed to create signed URL");
println!("Download URL: {:?}", response);
```

### Checking Available Credits

You can check the remaining credits on your account:

```rust
let credits = spider.get_credits().await.expect("Failed to get credits");
println!("Remaining Credits: {:?}", credits);
```

### Data Operations

The Spider client can now interact with specific data tables to create, retrieve, and delete data.

#### Retrieve Data from a Table

To fetch data from a specified table by applying query parameters:

```rust
let table_name = "pages";
let query_params = RequestParams {
    limit: Some(20),
    ..Default::default()
};
let response = spider.data_get(table_name, Some(query_params)).await.expect("Failed to retrieve data from table");
println!("Data from table: {:?}", response);
```

#### Delete Data from a Table

To delete data from a specified table based on certain conditions:

```rust
let table_name = "websites";
let delete_params = RequestParams {
    domain: Some("www.example.com".to_string()),
    ..Default::default()
};
let response = spider.data_delete(table_name, Some(delete_params)).await.expect("Failed to delete data from table");
println!("Delete Response: {:?}", response);
```

## Streaming

If you need to use streaming, set the `stream` parameter to `true` and provide a callback function:

```rust
fn handle_json(json_obj: serde_json::Value) {
    println!("Received chunk: {:?}", json_obj);
}

let url = "https://example.com";
let crawler_params = RequestParams {
    limit: Some(1),
    proxy_enabled: Some(true),
    metadata: Some(false),
    request: Some(RequestType::Http),
    ..Default::default()
};

spider.links(url, Some(crawler_params), true, "application/json").await.expect("Failed to retrieve links from URL");
```

## Content-Type

The following Content-type headers are supported using the `content_type` parameter:

- `application/json`
- `text/csv`
- `application/xml`
- `application/jsonl`

```rust
let url = "https://example.com";

let crawler_params = RequestParams {
    limit: Some(1),
    proxy_enabled: Some(true),
    metadata: Some(false),
    request: Some(RequestType::Http),
    ..Default::default()
};

// Stream JSON lines back to the client
spider.crawl_url(url, Some(crawler_params), true, "application/jsonl", None::<fn(serde_json::Value)>).await.expect("Failed to crawl the URL");
```

## Error Handling

The SDK handles errors returned by the Spider Cloud API and raises appropriate exceptions. If an error occurs during a request, it will be propagated to the caller with a descriptive error message.

## Features

1. `csv` handling content-type responses.
1. `xml` handling content-type responses.

## Contributing

Contributions to the Spider Cloud Rust SDK are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## License

The Spider Cloud Rust SDK is open-source and released under the [MIT License](https://opensource.org/licenses/MIT).
