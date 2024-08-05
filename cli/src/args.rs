use clap::{Parser, Subcommand};

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
    },
    /// Fetch all links from a given URL
    Links {
        #[arg(short, long, help = "The URL to fetch links from")]
        url: String,
    },
    /// Take a screenshot of a given URL
    Screenshot {
        #[arg(short, long, help = "The URL to take a screenshot of")]
        url: String,
    },
    /// Search using a given query
    Search {
        #[arg(short, long, help = "The query to search for")]
        query: String,
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
    },
    /// Label data from a given URL
    Label {
        #[arg(short, long, help = "The URL to label data from")]
        url: String,
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
