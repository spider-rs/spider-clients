use clap::{Parser, Subcommand, ValueEnum};
use serde::{Serialize, Deserialize};

#[derive(
    Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, ValueEnum
)]
#[serde(rename_all = "snake_case")]
pub enum ProxyType {
    /// Cost-effective entry-level residential pool.
    Residential,
    /// Higher-throughput residential pool.
    ResidentialFast,
    /// Static residential IPs, rotated daily.
    ResidentialStatic,
    /// 4G / 5G mobile proxies for stealth.
    Mobile,
    /// ISP-grade / datacenter-like routing.
    Isp,
    /// Premium low-latency residential pool.
    ResidentialPremium,
    /// Balanced plan (cost vs. quality).
    ResidentialCore,
    /// Largest, highest-quality IP pool.
    ResidentialPlus,
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
        #[arg(long, help = "Select proxy pool (e.g. residential, mobile, isp)", value_enum)]
        proxy: Option<ProxyType>,
        #[arg(long, help = "Use a remote proxy at ~70% reduced cost for file downloads.")]
        remote_proxy: Option<String>,
        #[arg(
            short,
            long,
            help = "Runs the request using lite_mode:Lite mode reduces data transfer costs by 70%, with trade-offs in speed, accuracy, geo-targeting, and reliability.",
            required = false
        )]
        lite_mode: Option<bool>,
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
        #[arg(long, help = "Select proxy pool (e.g. residential, mobile, isp)", value_enum)]
        proxy: Option<ProxyType>,
        #[arg(long, help = "Use a remote proxy at ~70% reduced cost for file downloads.")]
        remote_proxy: Option<String>,
        #[arg(
            short,
            long,
            help = "Returns the link(s) found on the page that match the crawler query.",
            required = false
        )]
        return_page_links: Option<bool>,
        #[arg(
            short,
            long,
            help = "Runs the request using lite_mode:Lite mode reduces data transfer costs by 70%, with trade-offs in speed, accuracy, geo-targeting, and reliability.",
            required = false
        )]
        lite_mode: Option<bool>,
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
        #[arg(long, help = "Select proxy pool (e.g. residential, mobile, isp)", value_enum)]
        proxy: Option<ProxyType>,
        #[arg(long, help = "Use a remote proxy at ~70% reduced cost for file downloads.")]
        remote_proxy: Option<String>,
        #[arg(
            short,
            long,
            help = "Returns the link(s) found on the page that match the crawler query.",
            required = false
        )]
        return_page_links: Option<bool>,
        #[arg(
            short,
            long,
            help = "Runs the request using lite_mode:Lite mode reduces data transfer costs by 70%, with trade-offs in speed, accuracy, geo-targeting, and reliability.",
            required = false
        )]
        lite_mode: Option<bool>,
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
        #[arg(long, help = "Select proxy pool (e.g. residential, mobile, isp)", value_enum)]
        proxy: Option<ProxyType>,
        #[arg(long, help = "Use a remote proxy at ~70% reduced cost for file downloads.")]
        remote_proxy: Option<String>,
        #[arg(
            short,
            long,
            help = "Returns the link(s) found on the page that match the crawler query.",
            required = false
        )]
        return_page_links: Option<bool>,
        #[arg(
            short,
            long,
            help = "Runs the request using lite_mode:Lite mode reduces data transfer costs by 70%, with trade-offs in speed, accuracy, geo-targeting, and reliability.",
            required = false
        )]
        lite_mode: Option<bool>,
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
    },
    /// Transform the provided data
    Transform {
        #[arg(short, long, help = "The data to transform")]
        data: String,
    },
    /// Extract leads from a given URL
    ExtractLeads {
        #[arg(short, long, help = "The URL to extract leads from")]
        url: String,
        #[arg(
            short,
            long,
            help = "Limit the number of pages to crawl",
            required = false
        )]
        limit: Option<u32>,
    },
    /// Label data from a given URL
    Label {
        #[arg(short, long, help = "The URL to label data from")]
        url: String,
        #[arg(
            short,
            long,
            help = "Limit the number of pages to crawl",
            required = false
        )]
        limit: Option<u32>,
        #[arg(long, help = "Select proxy pool (e.g. residential, mobile, isp)", value_enum)]
        proxy: Option<ProxyType>,
        #[arg(long, help = "Use a remote proxy at ~70% reduced cost for file downloads.")]
        remote_proxy: Option<String>,
    },
    /// Get the crawl state of a given URL
    GetCrawlState {
        #[arg(short, long, help = "The URL to get the crawl state of")]
        url: String,
    },
    /// Query for a domain
    Query {
        #[arg(short, long, help = "The domain to query")]
        domain: String,
    },
    /// Get the remaining credits
    GetCredits,
    /// Authenticate using an API key
    Auth {
        #[arg(short, long, help = "The API key to authenticate")]
        api_key: String,
    },
}

impl From<ProxyType> for spider_client::ProxyType {
    fn from(p: ProxyType) -> Self {
        match p {
           ProxyType::Residential => Self::Residential,
           ProxyType::ResidentialFast => Self::ResidentialFast,
           ProxyType::ResidentialStatic => Self::ResidentialStatic,
           ProxyType::Mobile => Self::Mobile,
           ProxyType::Isp => Self::Isp,
           ProxyType::ResidentialPremium => Self::ResidentialPremium,
           ProxyType::ResidentialCore => Self::ResidentialCore,
            ProxyType::ResidentialPlus => Self::ResidentialPlus,
        }
    }
}