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
//! - **Link Gathering:** One of the primary objectives of Spider is to
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

use backon::ExponentialBuilder;
use backon::Retryable;
use reqwest::Client;
use reqwest::{Error, Response};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use tokio_stream::StreamExt;

/// Structure representing the Chunking algorithm dictionary.
#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct ChunkingAlgDict {
    /// The chunking algorithm to use, defined as a specific type.
    r#type: ChunkingType,
    /// The amount to chunk by.
    value: i32,
}

// The nested structures
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Timeout {
    /// The seconds up to 60.
    pub secs: u64,
    /// The nanoseconds.
    pub nanos: u32,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct IdleNetwork {
    /// The timeout to wait until.
    pub timeout: Timeout,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
#[serde(tag = "type", rename_all = "PascalCase")]
pub enum WebAutomation {
    Evaluate { code: String },
    Click { selector: String },
    Wait { duration: u64 },
    WaitForNavigation,
    WaitFor { selector: String },
    WaitForAndClick { selector: String },
    ScrollX { pixels: i32 },
    ScrollY { pixels: i32 },
    Fill { selector: String, value: String },
    InfiniteScroll { times: u32 },
}

#[derive(Default, Serialize, Deserialize, Debug, Clone)]
#[serde(tag = "type", rename_all = "PascalCase")]
pub enum RedirectPolicy {
    Loose,
    #[default]
    Strict,
}

pub type WebAutomationMap = std::collections::HashMap<String, Vec<WebAutomation>>;
pub type ExecutionScriptsMap = std::collections::HashMap<String, String>;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Selector {
    /// The timeout to wait until.
    pub timeout: Timeout,
    /// The selector to wait for.
    pub selector: String,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Delay {
    /// The timeout to wait until.
    pub timeout: Timeout,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct WaitFor {
    /// Wait until idle networks with a timeout of idleness.
    pub idle_network: Option<IdleNetwork>,
    /// Wait until a selector exist. Can determine if a selector exist after executing all js and network events.
    pub selector: Option<Selector>,
    /// Wait until a hard delay.
    pub delay: Option<Delay>,
    /// Wait until page navigation happen. Default is true.
    pub page_navigations: Option<bool>,
}

/// Query request to get a document.
#[derive(Serialize, Deserialize, Debug, Clone, Default)]
pub struct QueryRequest {
    /// The exact website url.
    pub url: Option<String>,
    /// The website domain.
    pub domain: Option<String>,
    /// The path of the resource.
    pub pathname: Option<String>,
}

/// Enum representing different types of Chunking.
#[derive(Default, Debug, Deserialize, Serialize, Clone)]
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

#[derive(Default, Debug, Deserialize, Serialize, Clone)]
/// View port handling for chrome.
pub struct Viewport {
    /// Device screen Width
    pub width: u32,
    /// Device screen size
    pub height: u32,
    /// Device scale factor
    pub device_scale_factor: Option<f64>,
    /// Emulating Mobile?
    pub emulating_mobile: bool,
    /// Use landscape mode instead of portrait.
    pub is_landscape: bool,
    /// Touch screen device?
    pub has_touch: bool,
}

/// The API url.
const API_URL: &'static str = "https://api.spider.cloud";

// Define the CSSSelector struct
#[derive(Debug, Clone, Default, Deserialize, Serialize)]
pub struct CSSSelector {
    /// The name of the selector group
    pub name: String,
    /// A vector of CSS selectors
    pub selectors: Vec<String>,
}

// Define the CSSExtractionMap type
pub type CSSExtractionMap = HashMap<String, Vec<CSSSelector>>;

/// Represents the settings for a webhook configuration
#[derive(Debug, Default, Deserialize, Serialize, Clone)]
pub struct WebhookSettings {
    /// The destination where the webhook information will be sent
    destination: String,
    /// Trigger an action when all credits are depleted
    on_credits_depleted: bool,
    /// Trigger an action when half of the credits are depleted
    on_credits_half_depleted: bool,
    /// Trigger an action on a website status update event
    on_website_status: bool,
    /// Send information about a new page find (such as links and bytes)
    on_find: bool,
    /// Handle the metadata of a found page
    on_find_metadata: bool,
}

/// Send multiple return formats.
#[derive(Debug, Deserialize, Serialize, Clone)]
#[serde(untagged)]
pub enum ReturnFormatHandling {
    /// A single return item.
    Single(ReturnFormat),
    /// Multiple return formats.
    Multi(std::collections::HashSet<ReturnFormat>),
}

impl Default for ReturnFormatHandling {
    fn default() -> ReturnFormatHandling {
        ReturnFormatHandling::Single(ReturnFormat::Raw)
    }
}

/// Structure representing request parameters.
#[derive(Debug, Default, Deserialize, Serialize, Clone)]
pub struct RequestParams {
    #[serde(default)]
    /// The URL to be crawled.
    pub url: Option<String>,
    #[serde(default)]
    /// The type of request to be made.
    pub request: Option<RequestType>,
    #[serde(default)]
    /// The maximum number of pages the crawler should visit.
    pub limit: Option<u32>,
    #[serde(default)]
    /// The format in which the result should be returned.
    pub return_format: Option<ReturnFormatHandling>,
    #[serde(default)]
    /// Specifies whether to only visit the top-level domain.
    pub tld: Option<bool>,
    #[serde(default)]
    /// The depth of the crawl.
    pub depth: Option<u32>,
    #[serde(default)]
    /// Specifies whether the request should be cached.
    pub cache: Option<bool>,
    #[serde(default)]
    /// Perform an infinite scroll on the page as new content arises. The request param also needs to be set to 'chrome' or 'smart'.
    pub scroll: Option<u32>,
    #[serde(default)]
    /// The budget for various resources.
    pub budget: Option<HashMap<String, u32>>,
    #[serde(default)]
    /// The blacklist routes to ignore. This can be a Regex string pattern.
    pub blacklist: Option<Vec<String>>,
    #[serde(default)]
    /// The whitelist routes to only crawl. This can be a Regex string pattern and used with black_listing.
    pub whitelist: Option<Vec<String>>,
    #[serde(default)]
    /// The locale to be used during the crawl.
    pub locale: Option<String>,
    #[serde(default)]
    /// The cookies to be set for the request, formatted as a single string.
    pub cookies: Option<String>,
    #[serde(default)]
    /// Specifies whether to use stealth techniques to avoid detection.
    pub stealth: Option<bool>,
    #[serde(default)]
    /// The headers to be used for the request.
    pub headers: Option<HashMap<String, String>>,
    #[serde(default)]
    /// Specifies whether anti-bot measures should be used.
    pub anti_bot: Option<bool>,
    #[serde(default)]
    /// Specifies whether to send data via webhooks.
    pub webhooks: Option<WebhookSettings>,
    #[serde(default)]
    /// Specifies whether to include metadata in the response.
    pub metadata: Option<bool>,
    #[serde(default)]
    /// The dimensions of the viewport.
    pub viewport: Option<Viewport>,
    #[serde(default)]
    /// The encoding to be used for the request.
    pub encoding: Option<String>,
    #[serde(default)]
    /// Specifies whether to include subdomains in the crawl.
    pub subdomains: Option<bool>,
    #[serde(default)]
    /// The user agent string to be used for the request.
    pub user_agent: Option<String>,
    #[serde(default)]
    /// Specifies whether the response data should be stored.
    pub store_data: Option<bool>,
    #[serde(default)]
    /// Configuration settings for GPT (general purpose texture mappings).
    pub gpt_config: Option<HashMap<String, String>>,
    #[serde(default)]
    /// Specifies whether to use fingerprinting protection.
    pub fingerprint: Option<bool>,
    #[serde(default)]
    /// Specifies whether to perform the request without using storage.
    pub storageless: Option<bool>,
    #[serde(default)]
    /// Specifies whether readability optimizations should be applied.
    pub readability: Option<bool>,
    #[serde(default)]
    /// Specifies whether to use a proxy for the request.
    pub proxy_enabled: Option<bool>,
    #[serde(default)]
    /// Specifies whether to respect the site's robots.txt file.
    pub respect_robots: Option<bool>,
    #[serde(default)]
    /// CSS selector to be used to filter the content.
    pub root_selector: Option<String>,
    #[serde(default)]
    /// Specifies whether to load all resources of the crawl target.
    pub full_resources: Option<bool>,
    #[serde(default)]
    /// The text string to extract data from.
    pub text: Option<String>,
    #[serde(default)]
    /// Specifies whether to use the sitemap links.
    pub sitemap: Option<bool>,
    #[serde(default)]
    /// Get page insights to determine information like request duration, accessibility, and other web vitals. Requires the `metadata` parameter to be set to `true`.
    pub page_insights: Option<bool>,
    #[serde(default)]
    /// External domains to include the crawl.
    pub external_domains: Option<Vec<String>>,
    #[serde(default)]
    /// Returns the OpenAI embeddings for the title and description. Other values, such as keywords, may also be included. Requires the `metadata` parameter to be set to `true`.
    pub return_embeddings: Option<bool>,
    #[serde(default)]
    /// Returns the HTTP response headers.
    pub return_headers: Option<bool>,
    #[serde(default)]
    /// Returns the link(s) found on the page that match the crawler query.
    pub return_page_links: Option<bool>,
    #[serde(default)]
    /// Returns the HTTP response cookies.
    pub return_cookies: Option<bool>,
    #[serde(default)]
    /// The timeout for the request, in milliseconds.
    pub request_timeout: Option<u8>,
    #[serde(default)]
    /// Specifies whether to run the request in the background.
    pub run_in_background: Option<bool>,
    #[serde(default)]
    /// Specifies whether to skip configuration checks.
    pub skip_config_checks: Option<bool>,
    #[serde(default)]
    /// Use CSS query selectors to scrape contents from the web page. Set the paths and the CSS extraction object map to perform extractions per path or page.
    pub css_extraction_map: Option<CSSExtractionMap>,
    #[serde(default)]
    /// The chunking algorithm to use.
    pub chunking_alg: Option<ChunkingAlgDict>,
    /// Disable request interception when running 'request' as 'chrome' or 'smart'. This can help when the page uses 3rd party or external scripts to load content.
    pub disable_intercept: Option<bool>,
    /// The wait for events on the page. You need to make your `request` `chrome` or `smart`.
    pub wait_for: Option<WaitFor>,
    /// Perform custom Javascript tasks on a url or url path. You need to make your `request` `chrome` or `smart`
    pub execution_scripts: Option<ExecutionScriptsMap>,
    /// Perform web automated tasks on a url or url path. You need to make your `request` `chrome` or `smart`
    pub automation_scripts: Option<WebAutomationMap>,
    /// The redirect policy for HTTP request. Set the value to Loose to allow all.
    pub redirect_policy: Option<RedirectPolicy>,
}

/// The structure representing request parameters for a search request.
#[derive(Debug, Default, Deserialize, Serialize, Clone)]
pub struct SearchRequestParams {
    /// The base request parameters.
    #[serde(default, flatten)]
    pub base: RequestParams,
    // The search request.
    pub search: String,
    /// The search limit.
    pub search_limit: Option<u32>,
    // Fetch the page content. Defaults to true.
    pub fetch_page_content: Option<bool>,
    /// The search location of the request
    pub location: Option<String>,
    /// The country code of the request
    pub country: Option<String>,
    /// The language code of the request.
    pub language: Option<String>,
    /// The number of search results
    pub num: Option<u32>,
    /// The page of the search results.
    pub page: Option<u32>,
    #[serde(default)]
    /// The websites limit if a list is sent from text or urls comma split. This helps automatic configuration of the system.
    pub website_limit: Option<u32>,
}

/// Structure representing request parameters for transforming files.
#[derive(Debug, Default, Deserialize, Serialize, Clone)]
pub struct TransformParams {
    #[serde(default)]
    /// The format in which the result should be returned.
    pub return_format: Option<ReturnFormat>,
    #[serde(default)]
    /// Specifies whether readability optimizations should be applied.
    pub readability: Option<bool>,
    #[serde(default)]
    /// Clean the markdown or text for AI.
    pub clean: Option<bool>,
    #[serde(default)]
    /// Clean the markdown or text for AI removing footers, navigation, and more.
    pub clean_full: Option<bool>,
    /// The data being transformed.
    pub data: Vec<DataParam>,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct DataParam {
    /// The HTML resource.
    pub html: String,
    /// The website url.
    pub url: Option<String>,
}

/// the request type to perform
#[derive(Debug, Default, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum RequestType {
    /// Default HTTP request
    Http,
    /// Chrome browser rendering
    Chrome,
    #[default]
    /// Smart mode defaulting to HTTP and using Chrome when needed.
    SmartMode,
}

/// Enum representing different return formats.
#[derive(Default, Debug, Deserialize, Serialize, Clone, PartialEq, Eq, Hash)]
#[serde(rename_all = "lowercase")]
pub enum ReturnFormat {
    #[default]
    /// The default return format of the resource.
    Raw,
    /// Return the response as Markdown.
    Markdown,
    /// Return the response as Commonmark.
    Commonmark,
    /// Return the response as Html2text.
    Html2text,
    /// Return the response as Text.
    Text,
    /// Return the response as XML.
    Xml,
    /// Return the response as Bytes.
    Bytes,
}

/// Represents a Spider with API key and HTTP client.
#[derive(Debug, Default)]
pub struct Spider {
    /// The Spider API key.
    pub api_key: String,
    /// The Spider Client to re-use.
    pub client: Client,
}

impl Spider {
    /// Creates a new instance of Spider.
    ///
    /// # Arguments
    ///
    /// * `api_key` - An optional API key. Defaults to using the 'SPIDER_API_KEY' env variable.
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

    /// Creates a new instance of Spider.
    ///
    /// # Arguments
    ///
    /// * `api_key` - An optional API key. Defaults to using the 'SPIDER_API_KEY' env variable.
    /// * `client` - A custom client to pass in.
    ///
    /// # Returns
    ///
    /// A new instance of Spider or an error string if no API key is provided.
    pub fn new_with_client(api_key: Option<String>, client: Client) -> Result<Self, &'static str> {
        let api_key = api_key.or_else(|| std::env::var("SPIDER_API_KEY").ok());

        match api_key {
            Some(key) => Ok(Self {
                api_key: key,
                client,
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
    async fn api_post_base(
        &self,
        endpoint: &str,
        data: impl Serialize + Sized + std::fmt::Debug,
        content_type: &str,
    ) -> Result<Response, Error> {
        let url: String = format!("{API_URL}/{}", endpoint);

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
        data: impl Serialize + std::fmt::Debug + Clone + Send + Sync,
        content_type: &str,
    ) -> Result<Response, Error> {
        let fetch = || async {
            self.api_post_base(endpoint, data.to_owned(), content_type)
                .await
        };

        fetch
            .retry(ExponentialBuilder::default().with_max_times(5))
            .when(|err: &reqwest::Error| {
                if let Some(status) = err.status() {
                    status.is_server_error()
                } else {
                    err.is_timeout()
                }
            })
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
    async fn api_get_base<T: Serialize>(
        &self,
        endpoint: &str,
        query_params: Option<&T>,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let url = format!("{API_URL}/{}", endpoint);
        let res = self
            .client
            .get(&url)
            .query(&query_params)
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

    /// Sends a GET request to the API.
    ///
    /// # Arguments
    ///
    /// * `endpoint` - The API endpoint.
    ///
    /// # Returns
    ///
    /// The response from the API as a JSON value.
    async fn api_get<T: Serialize>(
        &self,
        endpoint: &str,
        query_params: Option<&T>,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let fetch = || async { self.api_get_base(endpoint, query_params.to_owned()).await };

        fetch
            .retry(ExponentialBuilder::default().with_max_times(5))
            .when(|err: &reqwest::Error| {
                if let Some(status) = err.status() {
                    status.is_server_error()
                } else {
                    err.is_timeout()
                }
            })
            .await
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
    async fn api_delete_base(
        &self,
        endpoint: &str,
        params: Option<HashMap<String, serde_json::Value>>,
    ) -> Result<Response, Error> {
        let url = format!("{API_URL}/v1/{}", endpoint);
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
        let fetch = || async { self.api_delete_base(endpoint, params.to_owned()).await };

        fetch
            .retry(ExponentialBuilder::default().with_max_times(5))
            .when(|err: &reqwest::Error| {
                if let Some(status) = err.status() {
                    status.is_server_error()
                } else {
                    err.is_timeout()
                }
            })
            .await
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
            if let Some(ref p) = params.as_object() {
                data.extend(p.iter().map(|(k, v)| (k.to_string(), v.clone())));
            }
        }

        let res = self.api_post("crawl", data, content_type).await?;
        res.json().await
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

        if let Ok(params) = serde_json::to_value(params) {
            if let Some(ref p) = params.as_object() {
                data.extend(p.iter().map(|(k, v)| (k.to_string(), v.clone())));
            }
        }

        data.insert("url".into(), serde_json::Value::String(url.to_string()));

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
        _stream: bool,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut data = HashMap::new();

        if let Ok(params) = serde_json::to_value(params) {
            if let Some(ref p) = params.as_object() {
                data.extend(p.iter().map(|(k, v)| (k.to_string(), v.clone())));
            }
        }

        data.insert("url".into(), serde_json::Value::String(url.to_string()));

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
        _stream: bool,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut data = HashMap::new();

        if let Ok(params) = serde_json::to_value(params) {
            if let Some(ref p) = params.as_object() {
                data.extend(p.iter().map(|(k, v)| (k.to_string(), v.clone())));
            }
        }

        data.insert("url".into(), serde_json::Value::String(url.to_string()));

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
        _stream: bool,
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
        data: Vec<HashMap<&str, &str>>,
        params: Option<TransformParams>,
        _stream: bool,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut payload = HashMap::new();

        if let Ok(params) = serde_json::to_value(params) {
            if let Some(ref p) = params.as_object() {
                payload.extend(p.iter().map(|(k, v)| (k.to_string(), v.clone())));
            }
        }

        if let Ok(d) = serde_json::to_value(data) {
            payload.insert("data".into(), d);
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
        _stream: bool,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut data = HashMap::new();

        if let Ok(params) = serde_json::to_value(params) {
            if let Ok(params) = serde_json::to_value(params) {
                if let Some(ref p) = params.as_object() {
                    data.extend(p.iter().map(|(k, v)| (k.to_string(), v.clone())));
                }
            }
        }

        match serde_json::to_value(url) {
            Ok(u) => {
                data.insert("url".into(), u);
            }
            _ => (),
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
        _stream: bool,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut data = HashMap::new();

        if let Ok(params) = serde_json::to_value(params) {
            if let Ok(params) = serde_json::to_value(params) {
                if let Some(ref p) = params.as_object() {
                    data.extend(p.iter().map(|(k, v)| (k.to_string(), v.clone())));
                }
            }
        }

        data.insert("url".into(), serde_json::Value::String(url.to_string()));

        let res = self.api_post("pipeline/label", data, content_type).await?;
        res.json().await
    }

    /// Download a record from storage.
    ///
    /// # Arguments
    ///
    /// * `url` - Optional exact url of the file in storage.
    /// * `options` - Optional options.
    /// * `stream` - Whether streaming is enabled.
    ///
    /// # Returns
    ///
    /// The response from the API.
    pub async fn download(
        &self,
        url: Option<&str>,
        options: Option<HashMap<&str, i32>>,
    ) -> Result<reqwest::Response, reqwest::Error> {
        let mut params = HashMap::new();

        if let Some(url) = url {
            params.insert("url".to_string(), url.to_string());
        }

        if let Some(options) = options {
            for (key, value) in options {
                params.insert(key.to_string(), value.to_string());
            }
        }

        let url = format!("{API_URL}/v1/data/download");
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

    /// Creates a signed URL of a file from storage.
    ///
    /// # Arguments
    ///
    /// * `url` - Optional exact url of the file in storage.
    /// * `options` - Optional options.
    /// * `stream` - Whether streaming is enabled.
    ///
    /// # Returns
    ///
    /// The response from the API.
    pub async fn create_signed_url(
        &self,
        url: Option<&str>,
        options: Option<HashMap<&str, i32>>,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut params = HashMap::new();

        if let Some(options) = options {
            for (key, value) in options {
                params.insert(key.to_string(), value.to_string());
            }
        }

        if let Some(url) = url {
            params.insert("url".to_string(), url.to_string());
        }

        let url = format!("{API_URL}/v1/data/sign-url");
        let request = self
            .client
            .get(&url)
            .header(
                "User-Agent",
                format!("Spider-Client/{}", env!("CARGO_PKG_VERSION")),
            )
            .header("Authorization", format!("Bearer {}", self.api_key))
            .query(&params);

        let res = request.send().await?;

        res.json().await
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
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut payload = HashMap::new();
        payload.insert("url".into(), serde_json::Value::String(url.to_string()));
        payload.insert(
            "contentType".into(),
            serde_json::Value::String(content_type.to_string()),
        );

        if let Ok(params) = serde_json::to_value(params) {
            if let Ok(params) = serde_json::to_value(params) {
                if let Some(ref p) = params.as_object() {
                    payload.extend(p.iter().map(|(k, v)| (k.to_string(), v.clone())));
                }
            }
        }

        let res = self
            .api_post("data/crawl_state", payload, content_type)
            .await?;
        res.json().await
    }

    /// Get the account credits left.
    pub async fn get_credits(&self) -> Result<serde_json::Value, reqwest::Error> {
        self.api_get::<serde_json::Value>("data/credits", None)
            .await
    }

    /// Send a request for a data record.
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

    /// Query a record from the global DB.
    pub async fn query(&self, params: &QueryRequest) -> Result<serde_json::Value, reqwest::Error> {
        let res = self
            .api_get::<QueryRequest>(&"data/query", Some(params))
            .await?;

        Ok(res)
    }

    /// Get a table record.
    pub async fn data_get(
        &self,
        table: &str,
        params: Option<RequestParams>,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut payload = HashMap::new();

        if let Some(params) = params {
            if let Ok(p) = serde_json::to_value(params) {
                if let Some(o) = p.as_object() {
                    payload.extend(o.iter().map(|(k, v)| (k.as_str(), v.clone())));
                }
            }
        }

        let res = self
            .api_get::<serde_json::Value>(&format!("data/{}", table), None)
            .await?;
        Ok(res)
    }

    /// Delete a record.
    pub async fn data_delete(
        &self,
        table: &str,
        params: Option<RequestParams>,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut payload = HashMap::new();

        if let Ok(params) = serde_json::to_value(params) {
            if let Ok(params) = serde_json::to_value(params) {
                if let Some(ref p) = params.as_object() {
                    payload.extend(p.iter().map(|(k, v)| (k.to_string(), v.clone())));
                }
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
    use reqwest::ClientBuilder;

    lazy_static! {
        static ref SPIDER_CLIENT: Spider = {
            dotenv().ok();
            let client = ClientBuilder::new();
            let client = client.user_agent("SpiderBot").build().unwrap();

            Spider::new_with_client(None, client).expect("client to build")
        };
    }

    #[tokio::test]
    #[ignore]
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
    #[ignore]
    async fn test_links() {
        let response: Result<serde_json::Value, Error> = SPIDER_CLIENT
            .links("https://example.com", None, false, "application/json")
            .await;
        assert!(response.is_ok());
    }

    #[tokio::test]
    #[ignore]
    async fn test_screenshot() {
        let mut params = RequestParams::default();
        params.limit = Some(1);

        let response = SPIDER_CLIENT
            .screenshot(
                "https://example.com",
                Some(params),
                false,
                "application/json",
            )
            .await;
        assert!(response.is_ok());
    }

    // #[tokio::test(flavor = "multi_thread")]
    // async fn test_search() {
    //     let mut params = SearchRequestParams::default();

    //     params.search_limit = Some(1);
    //     params.num = Some(1);
    //     params.fetch_page_content = Some(false);

    //     let response = SPIDER_CLIENT
    //         .search("a sports website", Some(params), false, "application/json")
    //         .await;

    //     assert!(response.is_ok());
    // }

    #[tokio::test]
    #[ignore]
    async fn test_transform() {
        let data = vec![HashMap::from([(
            "<html><body><h1>Transformation</h1></body></html>".into(),
            "".into(),
        )])];
        let response = SPIDER_CLIENT
            .transform(data, None, false, "application/json")
            .await;
        assert!(response.is_ok());
    }

    #[tokio::test]
    #[ignore]
    async fn test_extract_contacts() {
        let response = SPIDER_CLIENT
            .extract_contacts("https://example.com", None, false, "application/json")
            .await;
        assert!(response.is_ok());
    }

    #[tokio::test]
    #[ignore]
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
            .get_crawl_state("https://example.com", None, "application/json")
            .await;
        assert!(response.is_ok());
    }

    #[tokio::test]
    async fn test_query() {
        let mut query = QueryRequest::default();

        query.domain = Some("spider.cloud".into());

        let response = SPIDER_CLIENT.query(&query).await;
        assert!(response.is_ok());
    }

    #[tokio::test]
    async fn test_get_credits() {
        let response = SPIDER_CLIENT.get_credits().await;
        assert!(response.is_ok());
    }
}
