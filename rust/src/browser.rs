//! Browser automation via the `spider-browser` crate.
//!
//! Re-exports the [`spider_browser`] public types and provides a
//! [`Spider::browser`](crate::Spider::browser) constructor that creates a
//! [`SpiderBrowser`] pre-configured with the client's API key. The browser
//! connects to Spider's pre-warmed browser fleet over WebSocket (CDP/BiDi)
//! and supports deterministic page control as well as AI-powered
//! automation (act, observe, extract, agent).

use crate::Spider;

pub use spider_browser::ai::agent::{Agent, AgentOptions, AgentResult};
pub use spider_browser::ai::llm_provider::{LLMConfig, LLMProviderKind};
pub use spider_browser::ai::observe::ObserveResult;
pub use spider_browser::{SpiderBrowser, SpiderBrowserOptions, SpiderPage};

/// Options for a [`SpiderBrowser`] created via [`Spider::browser`].
///
/// The API key is injected from the [`Spider`] client, so it does not need
/// to be set here. Use the chainable `with_*` methods to configure the
/// browser:
///
/// ```rust,no_run
/// use spider_client::{BrowserOptions, Spider};
///
/// let spider = Spider::new(Some("myspiderapikey".into())).expect("API key must be provided");
/// let options = BrowserOptions::new()
///     .with_browser("chrome")
///     .with_stealth(2)
///     .with_country("US");
/// let browser = spider.browser(Some(options));
/// ```
#[derive(Debug, Clone)]
pub struct BrowserOptions(SpiderBrowserOptions);

impl Default for BrowserOptions {
    fn default() -> Self {
        Self(SpiderBrowserOptions::new(String::new()))
    }
}

impl BrowserOptions {
    /// Create a new set of browser options with defaults.
    pub fn new() -> Self {
        Self::default()
    }

    /// Set the browser type (e.g. "chrome", "firefox", "auto").
    pub fn with_browser(mut self, browser: impl Into<String>) -> Self {
        self.0.browser = Some(browser.into());
        self
    }

    /// Override the default WebSocket server URL.
    pub fn with_server_url(mut self, url: impl Into<String>) -> Self {
        self.0.server_url = Some(url.into());
        self
    }

    /// Set the initial stealth level (1-3, 0 = auto-escalate).
    pub fn with_stealth(mut self, level: u32) -> Self {
        self.0.stealth = Some(level);
        self
    }

    /// Set the LLM configuration for AI-powered actions.
    pub fn with_llm(mut self, config: LLMConfig) -> Self {
        self.0.llm = Some(config);
        self
    }

    /// Set the captcha handling mode ("off", "detect", "solve").
    pub fn with_captcha(mut self, mode: impl Into<String>) -> Self {
        self.0.captcha = Some(mode.into());
        self
    }

    /// Set the country code for geo-located proxies (e.g. "US", "GB").
    pub fn with_country(mut self, country: impl Into<String>) -> Self {
        self.0.country = Some(country.into());
        self
    }

    /// Set a custom proxy URL (e.g. "http://user:pass@proxy:8080").
    pub fn with_proxy_url(mut self, proxy_url: impl Into<String>) -> Self {
        self.0.proxy_url = Some(proxy_url.into());
        self
    }

    /// Enable or disable screencast recording.
    pub fn with_record(mut self, record: bool) -> Self {
        self.0.record = Some(record);
        self
    }

    /// Set the browser mode ("scraping" or "cua").
    pub fn with_mode(mut self, mode: impl Into<String>) -> Self {
        self.0.mode = Some(mode.into());
        self
    }
}

impl Spider {
    /// Create a new [`SpiderBrowser`] instance using this client's API key.
    /// The returned browser must be initialized with `init()` before use.
    ///
    /// ```rust,no_run
    /// use spider_client::{BrowserOptions, Spider};
    ///
    /// # #[ignore]
    /// #[tokio::main]
    /// async fn main() {
    ///     let spider = Spider::new(Some("myspiderapikey".into())).expect("API key must be provided");
    ///
    ///     let mut browser = spider.browser(Some(BrowserOptions::new().with_browser("chrome")));
    ///     browser.init().await.expect("Failed to connect to the browser fleet");
    ///
    ///     browser.page().goto("https://example.com").await.expect("Failed to navigate");
    ///     let html = browser.page().content(1_000, 0).await.expect("Failed to get the page content");
    ///     println!("{}", html);
    ///
    ///     browser.close();
    /// }
    /// ```
    pub fn browser(&self, options: Option<BrowserOptions>) -> SpiderBrowser {
        let mut opts = options.unwrap_or_default().0;
        opts.api_key = self.api_key.clone();
        SpiderBrowser::new(opts)
    }
}
