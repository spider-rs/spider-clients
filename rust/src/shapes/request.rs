use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Structure representing the Chunking algorithm dictionary.
#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct ChunkingAlgDict {
    /// The chunking algorithm to use, defined as a specific type.
    r#type: ChunkingType,
    /// The amount to chunk by.
    value: i32,
}

// The nested structures
#[derive(Serialize, Deserialize, Debug, Clone, Default)]
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

#[derive(Serialize, Deserialize, Debug, Clone, Default)]
pub struct Delay {
    /// The timeout to wait until.
    pub timeout: Timeout,
}

/// Default as true.
fn default_some_true() -> Option<bool> {
    Some(true)
}

#[derive(Serialize, Deserialize, Debug, Clone, Default)]
pub struct WaitFor {
    /// Wait until idle networks with a timeout of idleness.
    pub idle_network: Option<IdleNetwork>,
    /// Wait until a selector exist. Can determine if a selector exist after executing all js and network events.
    pub selector: Option<Selector>,
    /// Wait for the dom to update
    pub dom: Option<Selector>,
    /// Wait until a hard delay.
    pub delay: Option<Delay>,
    /// Wait until page navigation happen. Default is true.
    #[serde(default = "default_some_true")]
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

/// Proxy pool selection for outbound request routing.
/// Choose a pool based on your use case (e.g., stealth, speed, or stability).
///
/// - 'residential'         → cost-effective entry-level residential pool
/// - 'residential_fast'    → faster residential pool for higher throughput
/// - 'residential_static'  → static residential IPs, rotated daily
/// - 'residential_premium' → low-latency premium IPs
/// - 'residential_core'    → balanced plan (quality vs. cost)
/// - 'residential_plus'    → largest and highest quality core pool
/// - 'mobile'              → 4G/5G mobile proxies for maximum evasion
/// - 'isp'                 → ISP-grade datacenters
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize, Hash)]
pub enum ProxyType {
    /// Cost-effective entry-level residential pool.
    #[serde(rename = "residential")]
    Residential,
    /// Higher-throughput residential pool for better performance.
    #[serde(rename = "residential_fast")]
    ResidentialFast,
    /// Static residential IPs, rotated daily for session persistence.
    #[serde(rename = "residential_static")]
    ResidentialStatic,
    /// 4G / 5G mobile proxies for maximum stealth and evasion.
    #[serde(rename = "mobile")]
    Mobile,
    /// ISP-grade residential routing (alias: `datacenter`).
    #[serde(rename = "isp", alias = "datacenter")]
    #[default]
    Isp,
    /// Premium low-latency residential proxy pool.
    #[serde(rename = "residential_premium")]
    ResidentialPremium,
    /// Core residential plan optimized for balance between cost and quality.
    #[serde(rename = "residential_core")]
    ResidentialCore,
    /// Extended core residential pool with the largest, highest-quality IPs.
    #[serde(rename = "residential_plus")]
    ResidentialPlus,
}

/// List of proxies.
pub const PROXY_TYPE_LIST: [ProxyType; 10] = [
    ProxyType::ResidentialStatic,
    ProxyType::Residential,
    ProxyType::Isp,
    ProxyType::Mobile,
    ProxyType::ResidentialPremium,
    ProxyType::ResidentialPlus,
    ProxyType::ResidentialCore,
    ProxyType::ResidentialFast,
    ProxyType::ResidentialStatic,
    ProxyType::Residential,
];

impl ProxyType {
    /// Get the canonical string representation of the proxy type.
    pub fn as_str(&self) -> &'static str {
        match self {
            ProxyType::Residential => "residential",
            ProxyType::ResidentialFast => "residential_fast",
            ProxyType::ResidentialStatic => "residential_static",
            ProxyType::Mobile => "mobile",
            ProxyType::Isp => "isp",
            ProxyType::ResidentialPremium => "residential_premium",
            ProxyType::ResidentialCore => "residential_core",
            ProxyType::ResidentialPlus => "residential_plus",
        }
    }
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

#[derive(Debug, Default, Deserialize, Serialize, Clone)]
pub struct EventTracker {
    /// The responses received.
    responses: Option<bool>,
    ///The request sent.
    requests: Option<bool>,
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
    /// The country code for request
    pub country_code: Option<String>,
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
    /// Specifies whether to use a proxy for the request. [Deprecated]: use the 'proxy' param instead.
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
    /// The timeout for the request, in seconds.
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
    #[serde(default)]
    /// Disable request interception when running 'request' as 'chrome' or 'smart'. This can help when the page uses 3rd party or external scripts to load content.
    pub disable_intercept: Option<bool>,
    #[serde(default)]
    /// The wait for events on the page. You need to make your `request` `chrome` or `smart`.
    pub wait_for: Option<WaitFor>,
    #[serde(default)]
    /// Perform custom Javascript tasks on a url or url path. You need to make your `request` `chrome` or `smart`
    pub execution_scripts: Option<ExecutionScriptsMap>,
    #[serde(default)]
    /// Perform web automated tasks on a url or url path. You need to make your `request` `chrome` or `smart`
    pub automation_scripts: Option<WebAutomationMap>,
    #[serde(default)]
    /// The redirect policy for HTTP request. Set the value to Loose to allow all.
    pub redirect_policy: Option<RedirectPolicy>,
    #[serde(default)]
    /// Track the request sent and responses received for `chrome` or `smart`. The responses will track the bytes used and the requests will have the monotime sent.
    pub event_tracker: Option<EventTracker>,
    #[serde(default)]
    /// The timeout to stop the crawl.
    pub crawl_timeout: Option<Timeout>,
    #[serde(default)]
    /// Evaluates given script in every frame upon creation (before loading frame's scripts).
    pub evaluate_on_new_document: Option<Box<String>>,
    #[serde(default)]
    /// Runs the request using lite_mode:Lite mode reduces data transfer costs by 70%, with trade-offs in speed, accuracy,
    /// geo-targeting, and reliability. It’s best suited for non-urgent data collection or when
    /// targeting websites with minimal anti-bot protections.
    pub lite_mode: Option<bool>,
    #[serde(default)]
    /// The proxy to use for request.
    pub proxy: Option<ProxyType>,
    #[serde(default)]
    /// Use a remote proxy at ~70% reduced cost for file downloads.
    /// This requires a user-supplied static IP proxy endpoint.
    pub remote_proxy: Option<String>,
    #[serde(default)]
    /// Set the maximum number of credits to use per page.
    /// Credits are measured in decimal units, where 10,000 credits equal one dollar (100 credits per penny).
    /// Credit limiting only applies to request that are Javascript rendered using smart_mode or chrome for the 'request' type.
    pub max_credits_per_page: Option<f64>,
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
    /// Prioritize speed over output quantity.
    pub quick_search: Option<bool>
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
    /// Returns a screenshot as Base64Url
    Screenshot,
    /// Return the response as XML.
    Xml,
    /// Return the response as Bytes.
    Bytes,
}
