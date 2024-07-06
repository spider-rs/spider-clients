//! The `spider-client` module provides the primary interface and
//! functionalities for the Spider web crawler library, which is
//! designed for rapid and efficient crawling of web pages to gather
//! links using isolated contexts.
//!
//! ### Features
//!
//! - **Multi-threaded Crawling:** Spider can utilize multiple
//!   threads to parallelize the crawling process, drastically
//!   improving performance and allowing the ability to gather
//!   millions of pages in a short time.
//!
//! - **Configurable:** The library provides various options to
//!   configure the crawling behavior, such as setting the depth
//!   of crawling, user-agent strings, delays between requests,
//!   and more.
//!
//! - **Link Gathering:** The primary objective of Spider is to
//!   gather and manage links from the web pages it crawls,
//!   compiling them into a structured format for further use.
//!
//! ### Examples
//!
//! Basic usage of the Spider client might look like this:
//!
//! ```rust
//! use spider_client::{Spider, RequestType, RequestParams};
//! use tokio;
//! 
//!  # #[ignore]
//! #[tokio::main]
//! async fn main() {
//!     let spider = Spider::new(Some("myspiderapikey".into())).expect("API key must be provided");
//!
//!     let url = "https://spider.cloud";
//!
//!     // Scrape a single URL
//!     let scraped_data = spider.scrape_url(url, None, "application/json").await.expect("Failed to scrape the URL");
//!
//!     println!("Scraped Data: {:?}", scraped_data);
//!
//!     // Crawl a website
//!     let crawler_params = RequestParams {
//!         limit: Some(1),
//!         proxy_enabled: Some(true),
//!         store_data: Some(false),
//!         metadata: Some(false),
//!         request: Some(RequestType::Http),
//!         ..Default::default()
//!     };
//!
//!     let crawl_result = spider.crawl_url(url, Some(crawler_params), false, "application/json", None::<fn(serde_json::Value)>).await.expect("Failed to crawl the URL");
//!
//!     println!("Crawl Result: {:?}", crawl_result);
//! }
//! ```
//!
//! ### Modules
//!
//! - `config`: Contains the configuration options for the Spider client.
//! - `utils`: Utility functions used by the Spider client.
//!

use reqwest::Client;
use reqwest::{Error, Response};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use tokio_stream::StreamExt;

/// Structure representing the Chunking algorithm dictionary.
#[derive(Debug, Deserialize, Serialize)]
pub struct ChunkingAlgDict {
    /// The chunking algorithm to use, defined as a specific type.
    r#type: ChunkingType,
    /// The amount to chunk by.
    value: i32,
}

/// Enum representing different types of Chunking.
#[derive(Default, Debug, Deserialize, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum ChunkingType {
    #[default]
    /// By the word count.
    ByWords,
    /// By the line count.
    ByLines,
    /// By the char length.
    ByCharacterLength,
    /// By sentence.
    BySentence,
}

/// Structure representing request parameters.
#[derive(Debug, Default, Deserialize, Serialize)]
pub struct RequestParams {
    /// The URL to be crawled.
    pub url: Option<String>,
    /// The type of request to be made.
    pub request: Option<RequestType>,
    /// The maximum number of pages the crawler should visit.
    pub limit: Option<u32>,
    /// The format in which the result should be returned.
    pub return_format: Option<ReturnFormat>,
    /// Specifies whether to only visit the top-level domain.
    pub tld: Option<bool>,
    /// The depth of the crawl.
    pub depth: Option<u32>,
    /// Specifies whether the request should be cached.
    pub cache: Option<bool>,
    /// The budget for various resources.
    pub budget: Option<HashMap<String, u32>>,
    /// The blacklist routes to ignore. This can be a Regex string pattern.
    pub black_list: Option<Vec<String>>,
    /// The whitelist routes to only crawl. This can be a Regex string pattern and used with black_listing.
    pub white_list: Option<Vec<String>>,
    /// The locale to be used during the crawl.
    pub locale: Option<String>,
    /// The cookies to be set for the request, formatted as a single string.
    pub cookies: Option<String>,
    /// Specifies whether to use stealth techniques to avoid detection.
    pub stealth: Option<bool>,
    /// The headers to be used for the request.
    pub headers: Option<HashMap<String, String>>,
    /// Specifies whether anti-bot measures should be used.
    pub anti_bot: Option<bool>,
    /// Specifies whether to include metadata in the response.
    pub metadata: Option<bool>,
    /// The dimensions of the viewport.
    pub viewport: Option<HashMap<String, i32>>,
    /// The encoding to be used for the request.
    pub encoding: Option<String>,
    /// Specifies whether to include subdomains in the crawl.
    pub subdomains: Option<bool>,
    /// The user agent string to be used for the request.
    pub user_agent: Option<String>,
    /// Specifies whether the response data should be stored.
    pub store_data: Option<bool>,
    /// Configuration settings for GPT (general purpose texture mappings).
    pub gpt_config: Option<Vec<String>>,
    /// Specifies whether to use fingerprinting protection.
    pub fingerprint: Option<bool>,
    /// Specifies whether to perform the request without using storage.
    pub storageless: Option<bool>,
    /// Specifies whether readability optimizations should be applied.
    pub readability: Option<bool>,
    /// Specifies whether to use a proxy for the request.
    pub proxy_enabled: Option<bool>,
    /// Specifies whether to respect the site's robots.txt file.
    pub respect_robots: Option<bool>,
    /// CSS selector to be used to filter the content.
    pub query_selector: Option<String>,
    /// Specifies whether to load all resources of the crawl target.
    pub full_resources: Option<bool>,
    /// Specifies whether to use the sitemap links.
    pub sitemap: Option<bool>,
    /// Get page insights to determine information like request duration, accessibility, and other web vitals. Requires the `metadata` parameter to be set to `true`.
    pub page_insights: Option<bool>,
    /// Returns the OpenAI embeddings for the title and description. Other values, such as keywords, may also be included. Requires the `metadata` parameter to be set to `true`.
    pub return_embeddings: Option<bool>,
    /// The timeout for the request, in milliseconds.
    pub request_timeout: Option<u32>,
    /// Specifies whether to run the request in the background.
    pub run_in_background: Option<bool>,
    /// Specifies whether to skip configuration checks.
    pub skip_config_checks: Option<bool>,
    /// The chunking algorithm to use.
    pub chunking_alg: Option<ChunkingAlgDict>,
}

/// The structure representing request parameters for a search request.
#[derive(Debug, Default, Deserialize, Serialize)]
pub struct SearchRequestParams {
    /// The base request parameters.
    #[serde(flatten, skip)]
    pub base: RequestParams,
    /// The search query string.
    pub search: String,
    /// The limit amount of URLs to fetch or crawl from the search results.
    pub search_limit: Option<u32>,
    /// Fetch all the content of the websites by performing crawls.
    pub fetch_page_content: Option<bool>,
    /// The country code to use for the search. It's a two-letter country code (e.g., 'us' for the United States).
    pub country: Option<String>,
    /// The location from where you want the search to originate.
    pub location: Option<String>,
    /// The language to use for the search. It's a two-letter language code (e.g., 'en' for English).
    pub language: Option<String>,
    /// The maximum number of results to return for the search.
    pub num: Option<u32>,
}

/// Enum representing different types of Requests.
#[derive(Default, Debug, Deserialize, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum RequestType {
    #[default]
    Http,
    Chrome,
    Smart,
}

/// Enum representing different return formats.
#[derive(Default, Debug, Deserialize, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum ReturnFormat {
    #[default]
    Raw,
    Markdown,
    Commonmark,
    Html2text,
    Text,
    Bytes,
}

/// Represents a Spider with API key and HTTP client.
#[derive(Debug)]
pub struct Spider {
    /// The Spider API key.
    api_key: String,
    /// The Spider Client to re-use.
    client: Client,
}

impl Spider {
    /// Creates a new instance of Spider.
    ///
    /// # Arguments
    ///
    /// * `api_key` - An optional API key.
    ///
    /// # Returns
    ///
    /// A new instance of Spider or an error string if no API key is provided.
    pub fn new(api_key: Option<String>) -> Result<Self, &'static str> {
        let api_key = api_key.or_else(|| std::env::var("SPIDER_API_KEY").ok());

        match api_key {
            Some(key) => Ok(Self {
                api_key: key,
                client: Client::new(),
            }),
            None => Err("No API key provided"),
        }
    }

    /// Sends a POST request to the API.
    ///
    /// # Arguments
    ///
    /// * `endpoint` - The API endpoint.
    /// * `data` - The request data as a HashMap.
    /// * `stream` - Whether streaming is enabled.
    /// * `content_type` - The content type of the request.
    ///
    /// # Returns
    ///
    /// The response from the API.
    async fn api_post(
        &self,
        endpoint: &str,
        data: impl Serialize,
        content_type: &str,
    ) -> Result<Response, Error> {
        let url: String = format!("https://api.spider.cloud/{}", endpoint);
        self.client
            .post(&url)
            .header(
                "User-Agent",
                format!("Spider-Client/{}", env!("CARGO_PKG_VERSION")),
            )
            .header("Content-Type", content_type)
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(&data)
            .send()
            .await
    }

    /// Sends a GET request to the API.
    ///
    /// # Arguments
    ///
    /// * `endpoint` - The API endpoint.
    ///
    /// # Returns
    ///
    /// The response from the API as a JSON value.
    async fn api_get(&self, endpoint: &str) -> Result<serde_json::Value, reqwest::Error> {
        let url = format!("https://api.spider.cloud/{}", endpoint);
        let res = self
            .client
            .get(&url)
            .header(
                "User-Agent",
                format!("Spider-Client/{}", env!("CARGO_PKG_VERSION")),
            )
            .header("Content-Type", "application/json")
            .header("Authorization", format!("Bearer {}", self.api_key))
            .send()
            .await?;
        res.json().await
    }

    /// Scrapes a URL.
    ///
    /// # Arguments
    ///
    /// * `url` - The URL to scrape.
    /// * `params` - Optional request parameters.
    /// * `stream` - Whether streaming is enabled.
    /// * `content_type` - The content type of the request.
    ///
    /// # Returns
    ///
    /// The response from the API as a JSON value.
    pub async fn scrape_url(
        &self,
        url: &str,
        params: Option<RequestParams>,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut data = HashMap::new();

        data.insert(
            "url".to_string(),
            serde_json::Value::String(url.to_string()),
        );
        data.insert("limit".to_string(), serde_json::Value::Number(1.into()));

        if let Ok(params) = serde_json::to_value(params) {
            match params.as_object() {
                Some(ref p) => {
                    let params_collect = p.iter().map(|(k, v)| (k.to_string(), v.clone()));

                    data.extend(params_collect);
                }
                _ => (),
            }
        }

        let res = self.api_post("crawl", data, content_type).await?;
        res.json().await
    }

    /// Sends a DELETE request to the API.
    ///
    /// # Arguments
    ///
    /// * `endpoint` - The API endpoint.
    /// * `params` - Optional request parameters.
    /// * `stream` - Whether streaming is enabled.
    /// * `content_type` - The content type of the request.
    ///
    /// # Returns
    ///
    /// The response from the API.
    async fn api_delete(
        &self,
        endpoint: &str,
        params: Option<HashMap<String, serde_json::Value>>,
    ) -> Result<Response, Error> {
        let url = format!("https://api.spider.cloud/v1/{}", endpoint);
        let request_builder = self
            .client
            .delete(&url)
            .header(
                "User-Agent",
                format!("Spider-Client/{}", env!("CARGO_PKG_VERSION")),
            )
            .header("Content-Type", "application/json")
            .header("Authorization", format!("Bearer {}", self.api_key));

        let request_builder = if let Some(params) = params {
            request_builder.json(&params)
        } else {
            request_builder
        };

        request_builder.send().await
    }

    /// Crawls a URL.
    ///
    /// # Arguments
    ///
    /// * `url` - The URL to crawl.
    /// * `params` - Optional request parameters.
    /// * `stream` - Whether streaming is enabled.
    /// * `content_type` - The content type of the request.
    /// * `callback` - Optional callback function to handle each streamed chunk.
    ///
    /// # Returns
    ///
    /// The response from the API as a JSON value.
    pub async fn crawl_url(
        &self,
        url: &str,
        params: Option<RequestParams>,
        stream: bool,
        content_type: &str,
        callback: Option<impl Fn(serde_json::Value) + Send>,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut data = HashMap::new();
        data.insert("url".into(), serde_json::Value::String(url.to_string()));

        if let Ok(params) = serde_json::to_value(params) {
            match params.as_object() {
                Some(ref p) => {
                    data.extend(p.iter().map(|(k, v)| (k.to_string(), v.clone())));
                }
                _ => (),
            }
        }

        let res = self.api_post("crawl", data, content_type).await?;

        if stream {
            if let Some(callback) = callback {
                let stream = res.bytes_stream();
                tokio::pin!(stream);

                while let Some(item) = stream.next().await {
                    match item {
                        Ok(chunk) => match serde_json::from_slice(&chunk) {
                            Ok(json_obj) => {
                                callback(json_obj);
                            }
                            _ => (),
                        },
                        Err(e) => {
                            eprintln!("Error in streaming response: {}", e);
                        }
                    }
                }
                Ok(serde_json::Value::Null)
            } else {
                Ok(serde_json::Value::Null)
            }
        } else {
            res.json().await
        }
    }

    /// Fetches links from a URL.
    ///
    /// # Arguments
    ///
    /// * `url` - The URL to fetch links from.
    /// * `params` - Optional request parameters.
    /// * `stream` - Whether streaming is enabled.
    /// * `content_type` - The content type of the request.
    ///
    /// # Returns
    ///
    /// The response from the API as a JSON value.
    pub async fn links(
        &self,
        url: &str,
        params: Option<RequestParams>,
        stream: bool,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut data = HashMap::new();
        data.insert("url".into(), serde_json::Value::String(url.to_string()));
        if let Ok(params) = serde_json::to_value(params) {
            match params.as_object() {
                Some(ref p) => {
                    data.extend(p.iter().map(|(k, v)| (k.to_string(), v.clone())));
                }
                _ => (),
            }
        }

        let res = self.api_post("links", data, content_type).await?;
        res.json().await
    }

    /// Takes a screenshot of a URL.
    ///
    /// # Arguments
    ///
    /// * `url` - The URL to take a screenshot of.
    /// * `params` - Optional request parameters.
    /// * `stream` - Whether streaming is enabled.
    /// * `content_type` - The content type of the request.
    ///
    /// # Returns
    ///
    /// The response from the API as a JSON value.
    pub async fn screenshot(
        &self,
        url: &str,
        params: Option<RequestParams>,
        stream: bool,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut data = HashMap::new();
        data.insert("url".into(), serde_json::Value::String(url.to_string()));

        if let Ok(params) = serde_json::to_value(params) {
            match params.as_object() {
                Some(ref p) => {
                    data.extend(p.iter().map(|(k, v)| (k.to_string(), v.clone())));
                }
                _ => (),
            }
        }

        let res = self.api_post("screenshot", data, content_type).await?;
        res.json().await
    }

    /// Searches for a query.
    ///
    /// # Arguments
    ///
    /// * `q` - The query to search for.
    /// * `params` - Optional request parameters.
    /// * `stream` - Whether streaming is enabled.
    /// * `content_type` - The content type of the request.
    ///
    /// # Returns
    ///
    /// The response from the API as a JSON value.
    pub async fn search(
        &self,
        q: &str,
        params: Option<SearchRequestParams>,
        stream: bool,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let body = match params {
            Some(mut params) => {
                params.search = q.to_string();
                params
            }
            _ => {
                let mut params = SearchRequestParams::default();
                params.search = q.to_string();
                params
            }
        };

        let res = self.api_post("search", body, content_type).await?;
        
        res.json().await
    }

    /// Transforms data.
    ///
    /// # Arguments
    ///
    /// * `data` - The data to transform.
    /// * `params` - Optional request parameters.
    /// * `stream` - Whether streaming is enabled.
    /// * `content_type` - The content type of the request.
    ///
    /// # Returns
    ///
    /// The response from the API as a JSON value.
    pub async fn transform(
        &self,
        data: Vec<HashMap<&str, serde_json::Value>>,
        params: Option<RequestParams>,
        stream: bool,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut payload = HashMap::new();

        payload.insert("data".into(), serde_json::to_value(data).unwrap());

        if let Ok(params) = serde_json::to_value(params) {
            match params.as_object() {
                Some(ref p) => {
                    payload.extend(p.iter().map(|(k, v)| (k.to_string(), v.clone())));
                }
                _ => (),
            }
        }

        let res = self.api_post("transform", payload, content_type).await?;

        res.json().await
    }

    /// Extracts contacts from a URL.
    ///
    /// # Arguments
    ///
    /// * `url` - The URL to extract contacts from.
    /// * `params` - Optional request parameters.
    /// * `stream` - Whether streaming is enabled.
    /// * `content_type` - The content type of the request.
    ///
    /// # Returns
    ///
    /// The response from the API as a JSON value.
    pub async fn extract_contacts(
        &self,
        url: &str,
        params: Option<RequestParams>,
        stream: bool,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut data = HashMap::new();

        data.insert("url".into(), serde_json::to_value(url).unwrap());

        if let Ok(params) = serde_json::to_value(params) {
            match params.as_object() {
                Some(ref p) => {
                    data.extend(p.iter().map(|(k, v)| (k.to_string(), v.clone())));
                }
                _ => (),
            }
        }

        let res = self
            .api_post("pipeline/extract-contacts", data, content_type)
            .await?;
        res.json().await
    }

    /// Labels data from a URL.
    ///
    /// # Arguments
    ///
    /// * `url` - The URL to label data from.
    /// * `params` - Optional request parameters.
    /// * `stream` - Whether streaming is enabled.
    /// * `content_type` - The content type of the request.
    ///
    /// # Returns
    ///
    /// The response from the API as a JSON value.
    pub async fn label(
        &self,
        url: &str,
        params: Option<RequestParams>,
        stream: bool,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut data = HashMap::new();
        data.insert("url".into(), serde_json::Value::String(url.to_string()));

        if let Ok(params) = serde_json::to_value(params) {
            match params.as_object() {
                Some(ref p) => {
                    data.extend(p.iter().map(|(k, v)| (k.to_string(), v.clone())));
                }
                _ => (),
            }
        }

        let res = self.api_post("pipeline/label", data, content_type).await?;
        res.json().await
    }

    /// Creates a signed URL.
    ///
    /// # Arguments
    ///
    /// * `domain` - Optional domain.
    /// * `options` - Optional options.
    /// * `stream` - Whether streaming is enabled.
    ///
    /// # Returns
    ///
    /// The response from the API.
    pub async fn create_signed_url(
        &self,
        domain: Option<&str>,
        options: Option<HashMap<&str, i32>>,
    ) -> Result<reqwest::Response, reqwest::Error> {
        let mut params = HashMap::new();

        if let Some(domain) = domain {
            params.insert("domain".to_string(), domain.to_string());
        }

        if let Some(options) = options {
            for (key, value) in options {
                params.insert(key.to_string(), value.to_string());
            }
        }

        let url = format!("https://api.spider.cloud/v1/data/storage");
        let request = self
            .client
            .get(&url)
            .header(
                "User-Agent",
                format!("Spider-Client/{}", env!("CARGO_PKG_VERSION")),
            )
            .header("Content-Type", "application/octet-stream")
            .header("Authorization", format!("Bearer {}", self.api_key))
            .query(&params);

        let res = request.send().await?;

        Ok(res)
    }

    /// Gets the crawl state of a URL.
    ///
    /// # Arguments
    ///
    /// * `url` - The URL to get the crawl state of.
    /// * `params` - Optional request parameters.
    /// * `stream` - Whether streaming is enabled.
    /// * `content_type` - The content type of the request.
    ///
    /// # Returns
    ///
    pub async fn get_crawl_state(
        &self,
        url: &str,
        params: Option<RequestParams>,
        stream: bool,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut payload = HashMap::new();
        payload.insert("url".into(), serde_json::Value::String(url.to_string()));
        payload.insert(
            "contentType".into(),
            serde_json::Value::String(content_type.to_string()),
        );

        if let Ok(params) = serde_json::to_value(params) {
            match params.as_object() {
                Some(ref p) => {
                    payload.extend(p.iter().map(|(k, v)| (k.to_string(), v.clone())));
                }
                _ => (),
            }
        }

        let res = self
            .api_post("data/crawl_state", payload, content_type)
            .await?;
        res.json().await
    }

    pub async fn get_credits(&self) -> Result<serde_json::Value, reqwest::Error> {
        self.api_get("data/credits").await
    }

    pub async fn data_post(
        &self,
        table: &str,
        data: Option<RequestParams>,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let res = self
            .api_post(&format!("data/{}", table), data, "application/json")
            .await?;
        res.json().await
    }

    pub async fn data_get(
        &self,
        table: &str,
        params: Option<RequestParams>,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut payload = HashMap::new();

        if let Some(params) = params {
            let params = serde_json::to_value(params).unwrap();
            payload.extend(
                params
                    .as_object()
                    .unwrap()
                    .iter()
                    .map(|(k, v)| (k.as_str(), v.clone())),
            );
        }

        let res = self.api_get(&format!("data/{}", table)).await?;
        Ok(res)
    }

    pub async fn data_delete(
        &self,
        table: &str,
        params: Option<RequestParams>,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut payload = HashMap::new();

        if let Ok(params) = serde_json::to_value(params) {
            match params.as_object() {
                Some(ref p) => {
                    let params_collect = p.iter().map(|(k, v)| (k.to_string(), v.clone()));

                    payload.extend(params_collect);
                }
                _ => (),
            }
        }

        let res = self
            .api_delete(&format!("data/{}", table), Some(payload))
            .await?;
        res.json().await
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use dotenv::dotenv;
    use lazy_static::lazy_static;

    lazy_static! {
        static ref SPIDER_CLIENT: Spider = {
            dotenv().ok();
            Spider::new(None).unwrap()
        };
    }

    #[tokio::test]
    async fn test_scrape_url() {
        let response = SPIDER_CLIENT
            .scrape_url("https://example.com", None, "application/json")
            .await;
        assert!(response.is_ok());
    }

    #[tokio::test]
    async fn test_crawl_url() {
        let response = SPIDER_CLIENT
            .crawl_url(
                "https://example.com",
                None,
                false,
                "application/json",
                None::<fn(serde_json::Value)>,
            )
            .await;
        assert!(response.is_ok());
    }

    #[tokio::test]
    async fn test_links() {
        let response = SPIDER_CLIENT
            .links("https://example.com", None, false, "application/json")
            .await;
        assert!(response.is_ok());
    }

    #[tokio::test]
    async fn test_screenshot() {
        let response = SPIDER_CLIENT
            .screenshot("https://example.com", None, false, "application/json")
            .await;
        assert!(response.is_ok());
    }

    // #[tokio::test]
    // async fn test_search() {
    //     let mut params = SearchRequestParams::default();
    //     params.search_limit = Some(1);
    //     params.num = Some(1);

    //     let response = SPIDER_CLIENT
    //         .search("a sports website", Some(params), false, "application/json")
    //         .await;
    //     assert!(response.is_ok());
    // }

    // #[tokio::test]
    // async fn test_transform() {
    //     let data = vec![HashMap::new()];
    //     let response = SPIDER_CLIENT
    //         .transform(data, None, false, "application/json")
    //         .await;
    //     assert!(response.is_ok());
    // }

    #[tokio::test]
    async fn test_extract_contacts() {
        let response = SPIDER_CLIENT
            .extract_contacts("https://example.com", None, false, "application/json")
            .await;
        assert!(response.is_ok());
    }

    #[tokio::test]
    async fn test_label() {
        let response = SPIDER_CLIENT
            .label("https://example.com", None, false, "application/json")
            .await;
        assert!(response.is_ok());
    }

    #[tokio::test]
    async fn test_create_signed_url() {
        let response = SPIDER_CLIENT
            .create_signed_url(Some("example.com"), None)
            .await;
        assert!(response.is_ok());
    }

    #[tokio::test]
    async fn test_get_crawl_state() {
        let response = SPIDER_CLIENT
            .get_crawl_state("https://example.com", None, false, "application/json")
            .await;
        assert!(response.is_ok());
    }

    #[tokio::test]
    async fn test_get_credits() {
        let response = SPIDER_CLIENT.get_credits().await;
        assert!(response.is_ok());
    }
}
