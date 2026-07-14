use clap::{Parser, Subcommand, ValueEnum};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, ValueEnum)]
#[serde(rename_all = "snake_case")]
pub enum ProxyType {
    /// Cost-effective entry-level residential pool.
    Residential,
    /// 4G / 5G mobile proxies for stealth.
    Mobile,
    /// ISP-grade / datacenter-like routing.
    Isp,
}

#[derive(Parser, Debug)]
#[command(name = "Spider CLI")]
#[command(version = "1.0")]
#[command(about = "A CLI interface for the Spider web crawler")]
pub struct Cli {
    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Subcommand, Debug)]
pub enum Commands {
    /// Scrape a given URL
    Scrape {
        #[arg(short, long, help = "The URL to scrape")]
        url: String,
        #[arg(
            short,
            long,
            help = "Returns the link(s) found on the page that match the crawler query.",
            required = false
        )]
        return_page_links: Option<bool>,
        #[arg(
            long,
            help = "Select proxy pool (e.g. residential, mobile, isp)",
            value_enum
        )]
        proxy: Option<ProxyType>,
        #[arg(
            long,
            help = "Use a remote proxy at ~50% reduced cost for file downloads."
        )]
        remote_proxy: Option<String>,
    },
    /// Crawl a given URL with an optional page limit
    Crawl {
        #[arg(short, long, help = "The URL to crawl")]
        url: String,
        #[arg(
            short,
            long,
            help = "Limit the number of pages to crawl",
            required = false
        )]
        limit: Option<u32>,
        #[arg(
            long,
            help = "Select proxy pool (e.g. residential, mobile, isp)",
            value_enum
        )]
        proxy: Option<ProxyType>,
        #[arg(
            long,
            help = "Use a remote proxy at ~50% reduced cost for file downloads."
        )]
        remote_proxy: Option<String>,
        #[arg(
            short,
            long,
            help = "Returns the link(s) found on the page that match the crawler query.",
            required = false
        )]
        return_page_links: Option<bool>,
    },
    /// Fetch all links from a given URL
    Links {
        #[arg(short, long, help = "The URL to fetch links from")]
        url: String,
        #[arg(
            short,
            long,
            help = "Limit the number of pages to crawl",
            required = false
        )]
        limit: Option<u32>,
        #[arg(
            long,
            help = "Select proxy pool (e.g. residential, mobile, isp)",
            value_enum
        )]
        proxy: Option<ProxyType>,
        #[arg(
            long,
            help = "Use a remote proxy at ~50% reduced cost for file downloads."
        )]
        remote_proxy: Option<String>,
        #[arg(
            short,
            long,
            help = "Returns the link(s) found on the page that match the crawler query.",
            required = false
        )]
        return_page_links: Option<bool>,
    },
    /// Take a screenshot of a given URL
    Screenshot {
        #[arg(short, long, help = "The URL to take a screenshot of")]
        url: String,
        #[arg(
            short,
            long,
            help = "Limit the number of pages to crawl",
            required = false
        )]
        limit: Option<u32>,
        #[arg(
            long,
            help = "Select proxy pool (e.g. residential, mobile, isp)",
            value_enum
        )]
        proxy: Option<ProxyType>,
        #[arg(
            long,
            help = "Use a remote proxy at ~50% reduced cost for file downloads."
        )]
        remote_proxy: Option<String>,
        #[arg(
            short,
            long,
            help = "Returns the link(s) found on the page that match the crawler query.",
            required = false
        )]
        return_page_links: Option<bool>,
    },
    /// Search using a given query
    Search {
        #[arg(short, long, help = "The query to search for")]
        query: String,
        #[arg(
            short,
            long,
            help = "Limit the number of pages to crawl",
            required = false
        )]
        limit: Option<u32>,
        #[arg(
            short,
            long,
            help = "Returns the link(s) found on the page that match the crawler query.",
            required = false
        )]
        return_page_links: Option<bool>,
        #[arg(
            long,
            help = "Latitude for exact-coordinate localization (pair with --longitude).",
            required = false
        )]
        latitude: Option<f64>,
        #[arg(
            long,
            help = "Longitude for exact-coordinate localization (pair with --latitude).",
            required = false
        )]
        longitude: Option<f64>,
        #[arg(
            long,
            help = "Optional bias radius in meters for coordinate localization.",
            required = false
        )]
        radius: Option<i64>,
    },
    /// Unblock a given URL
    Unblocker {
        #[arg(short, long, help = "The URL to unblock")]
        url: String,
        #[arg(
            short,
            long,
            help = "Returns the link(s) found on the page that match the crawler query.",
            required = false
        )]
        return_page_links: Option<bool>,
        #[arg(
            long,
            help = "Select proxy pool (e.g. residential, mobile, isp)",
            value_enum
        )]
        proxy: Option<ProxyType>,
        #[arg(
            long,
            help = "Use a remote proxy at ~50% reduced cost for file downloads."
        )]
        remote_proxy: Option<String>,
    },
    /// Transform the provided data
    Transform {
        #[arg(short, long, help = "The data to transform")]
        data: String,
    },
    /// AI Studio endpoints (natural-language prompts). Requires an active AI Studio subscription: https://spider.cloud/ai/pricing
    Ai {
        #[command(subcommand)]
        command: AiCommands,
    },
    /// Unlimited-plan endpoints (flat-rate concurrency seats). Requires an active Unlimited subscription: https://spider.cloud/pricing?plan=unlimited
    Unlimited {
        #[command(subcommand)]
        command: UnlimitedCommands,
    },
    /// Get the remaining credits
    GetCredits,
    /// Authenticate using an API key
    Auth {
        #[arg(short, long, help = "The API key to authenticate")]
        api_key: String,
    },
}

/// AI Studio endpoints. Prompt-guided extraction billed separately from
/// credits — requires an active AI Studio subscription:
/// https://spider.cloud/ai/pricing
#[derive(Subcommand, Debug)]
pub enum AiCommands {
    /// AI-guided crawl of a website using a natural-language prompt
    Crawl {
        #[arg(short, long, help = "The URL to crawl")]
        url: String,
        #[arg(short, long, help = "Natural-language description of what to extract")]
        prompt: String,
        #[arg(
            short,
            long,
            help = "Limit the number of pages to crawl",
            required = false
        )]
        limit: Option<u32>,
        #[arg(
            long,
            help = "Select proxy pool (e.g. residential, mobile, isp)",
            value_enum
        )]
        proxy: Option<ProxyType>,
        #[arg(
            long,
            help = "Use a remote proxy at ~50% reduced cost for file downloads."
        )]
        remote_proxy: Option<String>,
    },
    /// AI-guided scrape of a single page using a natural-language prompt
    Scrape {
        #[arg(short, long, help = "The URL to scrape")]
        url: String,
        #[arg(short, long, help = "Natural-language description of what to extract")]
        prompt: String,
        #[arg(
            long,
            help = "Select proxy pool (e.g. residential, mobile, isp)",
            value_enum
        )]
        proxy: Option<ProxyType>,
        #[arg(
            long,
            help = "Use a remote proxy at ~50% reduced cost for file downloads."
        )]
        remote_proxy: Option<String>,
    },
    /// AI-enhanced web search using a natural-language prompt
    Search {
        #[arg(short, long, help = "Natural-language description of what to find")]
        prompt: String,
        #[arg(
            short,
            long,
            help = "Limit the number of results to return",
            required = false
        )]
        limit: Option<u32>,
    },
    /// AI-guided browser automation using a natural-language prompt
    Browser {
        #[arg(short, long, help = "The URL to automate")]
        url: String,
        #[arg(
            short,
            long,
            help = "Natural-language description of the browser actions"
        )]
        prompt: String,
    },
    /// AI-guided link extraction using a natural-language prompt
    Links {
        #[arg(short, long, help = "The URL to fetch links from")]
        url: String,
        #[arg(
            short,
            long,
            help = "Natural-language description of the links to return"
        )]
        prompt: String,
        #[arg(
            short,
            long,
            help = "Limit the number of pages to crawl",
            required = false
        )]
        limit: Option<u32>,
    },
}

/// Unlimited-plan endpoints. Flat monthly rate billed by purchased concurrency
/// seats instead of per-request credits — requires an active Unlimited
/// subscription: https://spider.cloud/pricing?plan=unlimited. AI/LLM extraction
/// params are not allowed on these routes.
#[derive(Subcommand, Debug)]
pub enum UnlimitedCommands {
    /// Scrape a single page on the Unlimited plan
    Scrape {
        #[arg(short, long, help = "The URL to scrape")]
        url: String,
        #[arg(
            short,
            long,
            help = "Returns the link(s) found on the page that match the crawler query.",
            required = false
        )]
        return_page_links: Option<bool>,
        #[arg(
            long,
            help = "Select proxy pool (e.g. residential, mobile, isp)",
            value_enum
        )]
        proxy: Option<ProxyType>,
        #[arg(
            long,
            help = "Use a remote proxy at ~50% reduced cost for file downloads."
        )]
        remote_proxy: Option<String>,
    },
    /// Crawl a website on the Unlimited plan with an optional page limit
    Crawl {
        #[arg(short, long, help = "The URL to crawl")]
        url: String,
        #[arg(
            short,
            long,
            help = "Limit the number of pages to crawl",
            required = false
        )]
        limit: Option<u32>,
        #[arg(
            long,
            help = "Select proxy pool (e.g. residential, mobile, isp)",
            value_enum
        )]
        proxy: Option<ProxyType>,
        #[arg(
            long,
            help = "Use a remote proxy at ~50% reduced cost for file downloads."
        )]
        remote_proxy: Option<String>,
        #[arg(
            short,
            long,
            help = "Returns the link(s) found on the page that match the crawler query.",
            required = false
        )]
        return_page_links: Option<bool>,
    },
    /// Fetch links from a website on the Unlimited plan
    Links {
        #[arg(short, long, help = "The URL to fetch links from")]
        url: String,
        #[arg(
            short,
            long,
            help = "Limit the number of pages to crawl",
            required = false
        )]
        limit: Option<u32>,
        #[arg(
            long,
            help = "Select proxy pool (e.g. residential, mobile, isp)",
            value_enum
        )]
        proxy: Option<ProxyType>,
        #[arg(
            long,
            help = "Use a remote proxy at ~50% reduced cost for file downloads."
        )]
        remote_proxy: Option<String>,
        #[arg(
            short,
            long,
            help = "Returns the link(s) found on the page that match the crawler query.",
            required = false
        )]
        return_page_links: Option<bool>,
    },
}

impl From<ProxyType> for spider_client::ProxyType {
    fn from(p: ProxyType) -> Self {
        match p {
            ProxyType::Residential => Self::Residential,
            ProxyType::Mobile => Self::Mobile,
            ProxyType::Isp => Self::Isp,
        }
    }
}
