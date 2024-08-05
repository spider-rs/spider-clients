mod args;
use args::{Cli, Commands};
use clap::Parser;
use keyring::Entry;
use serde_json::json;
use spider_client::{QueryRequest, RequestParams, SearchRequestParams, Spider};
use std::collections::HashMap;
use tokio;

const SERVICE_NAME: &str = "spider_client";
const USERNAME: &str = "default";

#[tokio::main]
async fn main() {
    let args = Cli::parse();
    let entry = Entry::new(SERVICE_NAME, USERNAME);

    match entry {
        Ok(ent) => {
            match args.command {
                Commands::Auth { ref api_key } => match ent.set_password(&api_key.trim()) {
                    Ok(_) => println!("API key saved successfully."),
                    Err(e) => eprintln!("Failed to save API key: {:?}", e),
                },
                _ => (),
            }

            match ent.get_password() {
                Ok(api_key) => {
                    let spider = Spider::new(Some(api_key.clone()))
                        .expect("Failed to initialize Spider client.");

                    match args.command {
                        Commands::Scrape { url } => {
                            println!("Scraping URL: {}", url);
                            match spider.scrape_url(&url, None, "application/json").await {
                                Ok(data) => println!("{}", json!(data)),
                                Err(e) => eprintln!("Error scraping URL: {:?}", e),
                            }
                        }
                        Commands::Crawl { url, limit } => {
                            println!("Crawling URL: {}", url);
                            let mut params = RequestParams::default();
                            if let Some(limit) = limit {
                                params.limit = Some(limit);
                            }
                            match spider
                                .crawl_url(
                                    &url,
                                    Some(params),
                                    false,
                                    "application/json",
                                    None::<fn(serde_json::Value)>,
                                )
                                .await
                            {
                                Ok(data) => println!("{}", json!(data)),
                                Err(e) => eprintln!("Error crawling URL: {:?}", e),
                            }
                        }
                        Commands::Links { url } => {
                            println!("Fetching links from URL: {}", url);
                            match spider.links(&url, None, false, "application/json").await {
                                Ok(data) => println!("{}", json!(data)),
                                Err(e) => eprintln!("Error fetching links: {:?}", e),
                            }
                        }
                        Commands::Screenshot { url } => {
                            let params = RequestParams::default();
                            println!("Taking screenshot of URL: {}", url);
                            match spider
                                .screenshot(&url, Some(params), false, "application/json")
                                .await
                            {
                                Ok(data) => println!("{}", json!(data)),
                                Err(e) => eprintln!("Error taking screenshot: {:?}", e),
                            }
                        }
                        Commands::Search { query } => {
                            let params = SearchRequestParams::default();
                            println!("Searching for query: {}", query);
                            match spider
                                .search(&query, Some(params), false, "application/json")
                                .await
                            {
                                Ok(data) => println!("{}", json!(data)),
                                Err(e) => eprintln!("Error searching for query: {:?}", e),
                            }
                        }
                        Commands::Transform { data } => {
                            let data_vec = vec![HashMap::from([("content", data.as_str())])];
                            println!("Transforming data: {}", data);
                            match spider
                                .transform(data_vec, None, false, "application/json")
                                .await
                            {
                                Ok(data) => println!("{}", json!(data)),
                                Err(e) => eprintln!("Error transforming data: {:?}", e),
                            }
                        }
                        Commands::ExtractLeads { url } => {
                            println!("Extracting leads from URL: {}", url);
                            match spider
                                .extract_contacts(&url, None, false, "application/json")
                                .await
                            {
                                Ok(data) => println!("{}", json!(data)),
                                Err(e) => eprintln!("Error extracting leads: {:?}", e),
                            }
                        }
                        Commands::Label { url } => {
                            println!("Labeling data from URL: {}", url);
                            match spider.label(&url, None, false, "application/json").await {
                                Ok(data) => println!("{}", json!(data)),
                                Err(e) => eprintln!("Error labeling data: {:?}", e),
                            }
                        }
                        Commands::GetCrawlState { url } => {
                            println!("Getting crawl state of URL: {}", url);
                            match spider.get_crawl_state(&url, None, "application/json").await {
                                Ok(data) => println!("{}", json!(data)),
                                Err(e) => eprintln!("Error getting crawl state: {:?}", e),
                            }
                        }
                        Commands::Query { domain } => {
                            let query = QueryRequest {
                                domain: Some(domain.to_string()),
                                ..Default::default()
                            };
                            println!("Querying record for domain: {}", domain);
                            match spider.query(&query).await {
                                Ok(data) => println!("{}", json!(data)),
                                Err(e) => eprintln!("Error querying record: {:?}", e),
                            }
                        }
                        Commands::GetCredits => {
                            println!("Fetching account credits left.");
                            match spider.get_credits().await {
                                Ok(data) => println!("{}", json!(data)),
                                Err(e) => eprintln!("Error fetching credits: {:?}", e),
                            }
                        }
                        _ => {}
                    }
                }
                Err(_) => {
                    eprintln!(
                        "No API key found. Please authenticate first using the `auth` command."
                    );
                }
            }
        }
        _ => (),
    }
}
