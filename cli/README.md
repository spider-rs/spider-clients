# Spider Cloud CLI

Spider Cloud CLI is a command-line interface to interact with the [Spider Cloud](https://spider.cloud) web crawler. It allows you to scrape, crawl, search, and perform various other web-related tasks through simple commands.

## Installation

Install the CLI using [`homebrew`](https://brew.sh/) or [`cargo`](https://doc.rust-lang.org/cargo/) from [crates.io](https://crates.io):

### Homebrew

```sh
brew tap spider-rs/spider-cloud-cli
brew install spider-cloud-cli
```

### Cargo

```sh
cargo install spider-cloud-cli
```

## Usage

After installing, you can use the CLI by typing `spider-cloud-cli` followed by a command and its respective arguments.

### Authentication

Before using most of the commands, you need to authenticate by providing an API key:

```sh
spider-cloud-cli auth --api-key YOUR_API_KEY
```

### Commands

#### Scrape

Scrape data from a specified URL.

```sh
spider-cloud-cli scrape --url http://example.com
```

#### Crawl

Crawl a specified URL with an optional limit on the number of pages.

```sh
spider-cloud-cli crawl --url http://example.com --limit 10
```

#### Links

Fetch links from a specified URL.

```sh
spider-cloud-cli links --url http://example.com
```

#### Screenshot

Take a screenshot of a specified URL.

```sh
spider-cloud-cli screenshot --url http://example.com
```

#### Search

Search for a query.

```sh
spider-cloud-cli search --query "example query"
```

#### Transform

Transform specified data.

```sh
spider-cloud-cli transform --data "sample data"
```

#### Get Credits

Fetch the account credits left.

```sh
spider-cloud-cli get_credits
```

### AI Studio Commands

Prompt-guided endpoints grouped under `ai`. These require an active AI Studio subscription, billed separately from credits — see [spider.cloud/ai/pricing](https://spider.cloud/ai/pricing).

```sh
spider-cloud-cli ai scrape --url http://example.com --prompt "Extract the product name and price"
spider-cloud-cli ai crawl --url http://example.com --prompt "Summarize each blog post" --limit 10
spider-cloud-cli ai search --prompt "Find the best Rust web crawlers"
spider-cloud-cli ai browser --url http://example.com --prompt "Click the pricing tab and read the plans"
spider-cloud-cli ai links --url http://example.com --prompt "Only the documentation links"
```

### Unlimited Commands

Flat-rate endpoints grouped under `unlimited`, billed by purchased concurrency seats rather than per-request credits. These require an active Unlimited subscription — see [spider.cloud/pricing?plan=unlimited](https://spider.cloud/pricing?plan=unlimited). When all purchased seats are in flight, requests return an immediate `429` with a `Retry-After` header (no queueing), so retry with backoff. AI/LLM extraction parameters are not accepted on these routes.

```sh
spider-cloud-cli unlimited scrape --url http://example.com
spider-cloud-cli unlimited crawl --url http://example.com --limit 10
spider-cloud-cli unlimited links --url http://example.com
```

See the [Unlimited API reference](https://spider.cloud/docs/api/unlimited) for details.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Issues and pull requests are welcome! Feel free to check the [issues page](https://github.com/spider-rs/spider-clients/issues) if you have any questions or suggestions.

## Acknowledgements

Special thanks to the developers and contributors of the libraries and tools used in this project.
