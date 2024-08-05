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
spider-cloud-cli auth --api_key YOUR_API_KEY
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

#### Extract Contacts

Extract contact information from a specified URL.

```sh
spider-cloud-cli extract_contacts --url http://example.com
```

#### Label

Label data from a specified URL.

```sh
spider-cloud-cli label --url http://example.com
```

#### Get Crawl State

Get the crawl state of a specified URL.

```sh
spider-cloud-cli get_crawl_state --url http://example.com
```

#### Query

Query records of a specified domain.

```sh
spider-cloud-cli query --domain example.com
```

#### Get Credits

Fetch the account credits left.

```sh
spider-cloud-cli get_credits
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Issues and pull requests are welcome! Feel free to check the [issues page](https://github.com/spider-rs/spider-clients/issues) if you have any questions or suggestions.

## Acknowledgements

Special thanks to the developers and contributors of the libraries and tools used in this project.
