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

pub mod shapes;

use backon::ExponentialBuilder;
use backon::Retryable;
use reqwest::Client;
use reqwest::{Error, Response};
use serde::Serialize;
pub use shapes::{request::*, response::*};
use std::collections::HashMap;
use std::sync::OnceLock;
use tokio_stream::StreamExt;

static API_URL: OnceLock<String> = OnceLock::new();

/// The API endpoint.
pub fn get_api_url() -> &'static str {
    API_URL.get_or_init(|| {
        std::env::var("SPIDER_API_URL").unwrap_or_else(|_| "https://api.spider.cloud".to_string())
    })
}

/// Represents a Spider with API key and HTTP client.
#[derive(Debug, Default)]
pub struct Spider {
    /// The Spider API key.
    pub api_key: String,
    /// The Spider Client to re-use.
    pub client: Client,
}

/// Handle the json response.
pub async fn handle_json(res: reqwest::Response) -> Result<serde_json::Value, reqwest::Error> {
    res.json().await
}

/// Handle the jsonl response.
pub async fn handle_jsonl(res: reqwest::Response) -> Result<serde_json::Value, reqwest::Error> {
    let text = res.text().await?;
    let lines = text
        .lines()
        .filter_map(|line| serde_json::from_str::<serde_json::Value>(line).ok())
        .collect::<Vec<_>>();
    Ok(serde_json::Value::Array(lines))
}

/// Handle the CSV response.
#[cfg(feature = "csv")]
pub async fn handle_csv(res: reqwest::Response) -> Result<serde_json::Value, reqwest::Error> {
    use std::collections::HashMap;
    let text = res.text().await?;
    let mut rdr = csv::Reader::from_reader(text.as_bytes());
    let records: Vec<HashMap<String, String>> = rdr.deserialize().filter_map(Result::ok).collect();

    if let Ok(record) = serde_json::to_value(records) {
        Ok(record)
    } else {
        Ok(serde_json::Value::String(text))
    }
}

#[cfg(not(feature = "csv"))]
pub async fn handle_csv(res: reqwest::Response) -> Result<serde_json::Value, reqwest::Error> {
    handle_text(res).await
}

/// Basic handle response to text
pub async fn handle_text(res: reqwest::Response) -> Result<serde_json::Value, reqwest::Error> {
    Ok(serde_json::Value::String(
        res.text().await.unwrap_or_default(),
    ))
}

/// Handle the XML response.
#[cfg(feature = "csv")]
pub async fn handle_xml(res: reqwest::Response) -> Result<serde_json::Value, reqwest::Error> {
    let text = res.text().await?;
    match quick_xml::de::from_str::<serde_json::Value>(&text) {
        Ok(val) => Ok(val),
        Err(_) => Ok(serde_json::Value::String(text)),
    }
}

#[cfg(not(feature = "csv"))]
/// Handle the XML response.
pub async fn handle_xml(res: reqwest::Response) -> Result<serde_json::Value, reqwest::Error> {
    handle_text(res).await
}

pub async fn parse_response(res: reqwest::Response) -> Result<serde_json::Value, reqwest::Error> {
    let content_type = res
        .headers()
        .get(reqwest::header::CONTENT_TYPE)
        .and_then(|v| v.to_str().ok())
        .unwrap_or_default()
        .to_ascii_lowercase();

    if content_type.contains("json") && !content_type.contains("jsonl") {
        handle_json(res).await
    } else if content_type.contains("jsonl") || content_type.contains("ndjson") {
        handle_jsonl(res).await
    } else if content_type.contains("csv") {
        handle_csv(res).await
    } else if content_type.contains("xml") {
        handle_xml(res).await
    } else {
        handle_text(res).await
    }
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
        let url: String = format!("{}/{}", get_api_url(), endpoint);

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
    pub async fn api_post(
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
        let url = format!("{}/{}", get_api_url(), endpoint);
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
        parse_response(res).await
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
    pub async fn api_get<T: Serialize>(
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
        let url = format!("{}/v1/{}", get_api_url(), endpoint);
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
    pub async fn api_delete(
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

        if let Ok(params) = serde_json::to_value(params) {
            if let Some(ref p) = params.as_object() {
                data.extend(p.iter().map(|(k, v)| (k.to_string(), v.clone())));
            }
        }

        if !url.is_empty() {
            data.insert(
                "url".to_string(),
                serde_json::Value::String(url.to_string()),
            );
        }

        let res = self.api_post("scrape", data, content_type).await?;
        parse_response(res).await
    }

    /// Scrapes multi URLs.
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
    pub async fn multi_scrape_url(
        &self,
        params: Option<Vec<RequestParams>>,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut data = HashMap::new();

        if let Ok(mut params) = serde_json::to_value(params) {
            if let Some(obj) = params.as_object_mut() {
                obj.insert("limit".to_string(), serde_json::Value::Number(1.into()));
                data.extend(obj.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
        }
        let res = self.api_post("scrape", data, content_type).await?;
        parse_response(res).await
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
        use tokio_util::codec::{FramedRead, LinesCodec};

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

                let stream_reader = tokio_util::io::StreamReader::new(
                    stream
                        .map(|r| r.map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))),
                );

                let mut lines = FramedRead::new(stream_reader, LinesCodec::new());

                while let Some(line_result) = lines.next().await {
                    match line_result {
                        Ok(line) => match serde_json::from_str::<serde_json::Value>(&line) {
                            Ok(value) => {
                                callback(value);
                            }
                            Err(_e) => {
                                continue;
                            }
                        },
                        Err(_e) => return Ok(serde_json::Value::Null),
                    }
                }

                Ok(serde_json::Value::Null)
            } else {
                Ok(serde_json::Value::Null)
            }
        } else {
            parse_response(res).await
        }
    }

    /// Crawls multiple URLs.
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
    pub async fn multi_crawl_url(
        &self,
        params: Option<Vec<RequestParams>>,
        stream: bool,
        content_type: &str,
        callback: Option<impl Fn(serde_json::Value) + Send>,
    ) -> Result<serde_json::Value, reqwest::Error> {
        use tokio_util::codec::{FramedRead, LinesCodec};

        let res = self.api_post("crawl", params, content_type).await?;

        if stream {
            if let Some(callback) = callback {
                let stream = res.bytes_stream();

                let stream_reader = tokio_util::io::StreamReader::new(
                    stream
                        .map(|r| r.map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))),
                );

                let mut lines = FramedRead::new(stream_reader, LinesCodec::new());

                while let Some(line_result) = lines.next().await {
                    match line_result {
                        Ok(line) => match serde_json::from_str::<serde_json::Value>(&line) {
                            Ok(value) => {
                                callback(value);
                            }
                            Err(_e) => {
                                continue;
                            }
                        },
                        Err(_e) => return Ok(serde_json::Value::Null),
                    }
                }

                Ok(serde_json::Value::Null)
            } else {
                Ok(serde_json::Value::Null)
            }
        } else {
            parse_response(res).await
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
        parse_response(res).await
    }

    /// Fetches links from a URLs.
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
    pub async fn multi_links(
        &self,
        params: Option<Vec<RequestParams>>,
        _stream: bool,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let res = self.api_post("links", params, content_type).await?;
        parse_response(res).await
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
        parse_response(res).await
    }

    /// Takes a screenshot of multiple URLs.
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
    pub async fn multi_screenshot(
        &self,
        params: Option<Vec<RequestParams>>,
        _stream: bool,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let res = self.api_post("screenshot", params, content_type).await?;
        parse_response(res).await
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

        parse_response(res).await
    }

    /// Searches for multiple querys.
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
    pub async fn multi_search(
        &self,
        params: Option<Vec<SearchRequestParams>>,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let res = self.api_post("search", params, content_type).await?;
        parse_response(res).await
    }

    /// Unblock a URL.
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
    pub async fn unblock_url(
        &self,
        url: &str,
        params: Option<RequestParams>,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut data = HashMap::new();

        if let Ok(params) = serde_json::to_value(params) {
            if let Some(ref p) = params.as_object() {
                data.extend(p.iter().map(|(k, v)| (k.to_string(), v.clone())));
            }
        }

        if !url.is_empty() {
            data.insert(
                "url".to_string(),
                serde_json::Value::String(url.to_string()),
            );
        }

        let res = self.api_post("unblocker", data, content_type).await?;
        parse_response(res).await
    }

    /// Unblock multi URLs.
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
    pub async fn multi_unblock_url(
        &self,
        params: Option<Vec<RequestParams>>,
        content_type: &str,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let mut data = HashMap::new();

        if let Ok(mut params) = serde_json::to_value(params) {
            if let Some(obj) = params.as_object_mut() {
                obj.insert("limit".to_string(), serde_json::Value::Number(1.into()));
                data.extend(obj.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
        }
        let res = self.api_post("unblocker", data, content_type).await?;
        parse_response(res).await
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

        parse_response(res).await
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
        parse_response(res).await
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
    async fn test_get_credits() {
        let response = SPIDER_CLIENT.get_credits().await;
        assert!(response.is_ok());
    }
}
