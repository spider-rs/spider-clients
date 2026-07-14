mod args;
use args::{AiCommands, Cli, Commands, UnlimitedCommands};
use clap::Parser;
use keyring::Entry;
use serde_json::json;
use spider_client::{RequestParams, SearchRequestParams, Spider};
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
                        Commands::Scrape {
                            url,
                            return_page_links,
                            proxy,
                            remote_proxy,
                        } => {
                            println!("Scraping URL: {}", url);
                            let mut params = RequestParams::default();
                            params.return_page_links = return_page_links;
                            params.proxy = proxy.map(Into::into);
                            params.remote_proxy = remote_proxy.map(Into::into);

                            match spider
                                .scrape_url(&url, Some(params), "application/json")
                                .await
                            {
                                Ok(data) => println!("{}", json!(data)),
                                Err(e) => eprintln!("Error scraping URL: {:?}", e),
                            }
                        }
                        Commands::Unblocker {
                            url,
                            return_page_links,
                            proxy,
                            remote_proxy,
                        } => {
                            println!("Unblocking URL: {}", url);
                            let mut params = RequestParams::default();
                            params.return_page_links = return_page_links;
                            params.proxy = proxy.map(Into::into);
                            params.remote_proxy = remote_proxy.map(Into::into);

                            match spider
                                .scrape_url(&url, Some(params), "application/json")
                                .await
                            {
                                Ok(data) => println!("{}", json!(data)),
                                Err(e) => eprintln!("Error scraping URL: {:?}", e),
                            }
                        }
                        Commands::Crawl {
                            url,
                            limit,
                            return_page_links,
                            proxy,
                            remote_proxy,
                        } => {
                            println!("Crawling URL: {}", url);
                            let mut params = RequestParams::default();
                            if let Some(limit) = limit {
                                params.limit = Some(limit);
                            }
                            params.return_page_links = return_page_links;
                            params.proxy = proxy.map(Into::into);
                            params.remote_proxy = remote_proxy.map(Into::into);
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
                        Commands::Links {
                            url,
                            return_page_links,
                            limit,
                            proxy,
                            remote_proxy,
                        } => {
                            println!("Fetching links from URL: {}", url);
                            let mut params = RequestParams::default();
                            if let Some(limit) = limit {
                                params.limit = Some(limit);
                            }
                            params.return_page_links = return_page_links;
                            params.proxy = proxy.map(Into::into);
                            params.remote_proxy = remote_proxy.map(Into::into);
                            match spider
                                .links(&url, Some(params), false, "application/json")
                                .await
                            {
                                Ok(data) => println!("{}", json!(data)),
                                Err(e) => eprintln!("Error fetching links: {:?}", e),
                            }
                        }
                        Commands::Screenshot {
                            url,
                            limit,
                            return_page_links,
                            proxy,
                            remote_proxy,
                        } => {
                            let mut params = RequestParams::default();
                            if let Some(limit) = limit {
                                params.limit = Some(limit);
                            }
                            params.return_page_links = return_page_links;
                            params.proxy = proxy.map(Into::into);
                            params.remote_proxy = remote_proxy.map(Into::into);
                            println!("Taking screenshot of URL: {}", url);
                            match spider
                                .screenshot(&url, Some(params), false, "application/json")
                                .await
                            {
                                Ok(data) => println!("{}", json!(data)),
                                Err(e) => eprintln!("Error taking screenshot: {:?}", e),
                            }
                        }
                        Commands::Search {
                            query,
                            limit,
                            return_page_links,
                            latitude,
                            longitude,
                            radius,
                        } => {
                            let mut params = SearchRequestParams::default();
                            if let Some(limit) = limit {
                                params.base.limit = Some(limit);
                            }
                            params.base.return_page_links = return_page_links;
                            params.latitude = latitude;
                            params.longitude = longitude;
                            params.radius = radius;
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
                        Commands::GetCredits => {
                            println!("Fetching account credits left.");
                            match spider.get_credits().await {
                                Ok(data) => println!("{}", json!(data)),
                                Err(e) => eprintln!("Error fetching credits: {:?}", e),
                            }
                        }
                        Commands::Ai { command } => match command {
                            AiCommands::Crawl {
                                url,
                                prompt,
                                limit,
                                proxy,
                                remote_proxy,
                            } => {
                                println!("AI crawling URL: {}", url);
                                let mut params = RequestParams::default();
                                if let Some(limit) = limit {
                                    params.limit = Some(limit);
                                }
                                params.proxy = proxy.map(Into::into);
                                params.remote_proxy = remote_proxy.map(Into::into);
                                match spider
                                    .ai_crawl(&url, &prompt, Some(params), "application/json")
                                    .await
                                {
                                    Ok(data) => println!("{}", json!(data)),
                                    Err(e) => eprintln!("Error with AI crawl: {:?}", e),
                                }
                            }
                            AiCommands::Scrape {
                                url,
                                prompt,
                                proxy,
                                remote_proxy,
                            } => {
                                println!("AI scraping URL: {}", url);
                                let mut params = RequestParams::default();
                                params.proxy = proxy.map(Into::into);
                                params.remote_proxy = remote_proxy.map(Into::into);
                                match spider
                                    .ai_scrape(&url, &prompt, Some(params), "application/json")
                                    .await
                                {
                                    Ok(data) => println!("{}", json!(data)),
                                    Err(e) => eprintln!("Error with AI scrape: {:?}", e),
                                }
                            }
                            AiCommands::Search { prompt, limit } => {
                                println!("AI searching for: {}", prompt);
                                let mut params = RequestParams::default();
                                if let Some(limit) = limit {
                                    params.limit = Some(limit);
                                }
                                match spider
                                    .ai_search(&prompt, Some(params), "application/json")
                                    .await
                                {
                                    Ok(data) => println!("{}", json!(data)),
                                    Err(e) => eprintln!("Error with AI search: {:?}", e),
                                }
                            }
                            AiCommands::Browser { url, prompt } => {
                                println!("AI browser automation on URL: {}", url);
                                let params = RequestParams::default();
                                match spider
                                    .ai_browser(&url, &prompt, Some(params), "application/json")
                                    .await
                                {
                                    Ok(data) => println!("{}", json!(data)),
                                    Err(e) => eprintln!("Error with AI browser: {:?}", e),
                                }
                            }
                            AiCommands::Links { url, prompt, limit } => {
                                println!("AI extracting links from URL: {}", url);
                                let mut params = RequestParams::default();
                                if let Some(limit) = limit {
                                    params.limit = Some(limit);
                                }
                                match spider
                                    .ai_links(&url, &prompt, Some(params), "application/json")
                                    .await
                                {
                                    Ok(data) => println!("{}", json!(data)),
                                    Err(e) => eprintln!("Error with AI links: {:?}", e),
                                }
                            }
                        },
                        Commands::Unlimited { command } => match command {
                            UnlimitedCommands::Scrape {
                                url,
                                return_page_links,
                                proxy,
                                remote_proxy,
                            } => {
                                println!("Unlimited scraping URL: {}", url);
                                let mut params = RequestParams::default();
                                params.return_page_links = return_page_links;
                                params.proxy = proxy.map(Into::into);
                                params.remote_proxy = remote_proxy.map(Into::into);
                                match spider
                                    .unlimited_scrape(&url, Some(params), "application/json")
                                    .await
                                {
                                    Ok(data) => println!("{}", json!(data)),
                                    Err(e) => eprintln!("Error with unlimited scrape: {:?}", e),
                                }
                            }
                            UnlimitedCommands::Crawl {
                                url,
                                limit,
                                proxy,
                                remote_proxy,
                                return_page_links,
                            } => {
                                println!("Unlimited crawling URL: {}", url);
                                let mut params = RequestParams::default();
                                if let Some(limit) = limit {
                                    params.limit = Some(limit);
                                }
                                params.return_page_links = return_page_links;
                                params.proxy = proxy.map(Into::into);
                                params.remote_proxy = remote_proxy.map(Into::into);
                                match spider
                                    .unlimited_crawl(
                                        &url,
                                        Some(params),
                                        false,
                                        "application/json",
                                        None::<fn(serde_json::Value)>,
                                    )
                                    .await
                                {
                                    Ok(data) => println!("{}", json!(data)),
                                    Err(e) => eprintln!("Error with unlimited crawl: {:?}", e),
                                }
                            }
                            UnlimitedCommands::Links {
                                url,
                                limit,
                                proxy,
                                remote_proxy,
                                return_page_links,
                            } => {
                                println!("Unlimited fetching links from URL: {}", url);
                                let mut params = RequestParams::default();
                                if let Some(limit) = limit {
                                    params.limit = Some(limit);
                                }
                                params.return_page_links = return_page_links;
                                params.proxy = proxy.map(Into::into);
                                params.remote_proxy = remote_proxy.map(Into::into);
                                match spider
                                    .unlimited_links(&url, Some(params), false, "application/json")
                                    .await
                                {
                                    Ok(data) => println!("{}", json!(data)),
                                    Err(e) => eprintln!("Error with unlimited links: {:?}", e),
                                }
                            }
                        },
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
