# SpiderWebAI Python SDK

The SpiderWebAI Python SDK offers a toolkit for straightforward website scraping and crawling at scale, enabling you to collect data formatted for compatibility with language models (LLMs). It features a user-friendly interface for seamless integration with the SpiderWebAI API.

## Installation

To install the spiderwebai Python SDK, you can use pip:

```bash
pip install spiderwebai-py
```

## Usage

1. Get an API key from [spiderwebai.xyz](https://spiderwebai.xyz)
2. Set the API key as an environment variable named `SPIDER_API_KEY` or pass it as a parameter to the `SpiderWebAIApp` class.

Here's an example of how to use the SDK:

```python
from spiderwebai import SpiderWebAIApp

# Initialize the SpiderWebAIApp with your API key
app = SpiderWebAIApp(api_key='your_api_key')

# Scrape a single URL
url = 'https://spiderwebai.xyz'
scraped_data = app.scrape_url(url)

# Crawl a website
crawl_url = 'https://spiderwebai.xyz'
params = {
    'limit': 1,
    'proxy_enabled': True,
    'store_data': False,
    'metadata': False,
    'request': 'http'
}
crawl_result = app.crawl_url(crawl_url, params=params)
```

### Scraping a URL

To scrape a single URL, use the `scrape_url` method. It takes the URL as a parameter and returns the scraped data as a dictionary.

```python
url = 'https://example.com'
scraped_data = app.scrape_url(url)
```

### Crawling a Website

To crawl a website, use the `crawl_url` method. It takes the starting URL and optional parameters as arguments. The `params` argument allows you to specify additional options for the crawl, such as the maximum number of pages to crawl, allowed domains, and the output format.

```python
crawl_url = 'https://example.com'
params = {
    'limit': 200,
    'request': 'smart_mode'
}
crawl_result = app.crawl_url(crawl_url, params=params)
```

## Error Handling

The SDK handles errors returned by the SpiderWebAI API and raises appropriate exceptions. If an error occurs during a request, an exception will be raised with a descriptive error message.

## Contributing

Contributions to the SpiderWebAI Python SDK are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## License

The SpiderWebAI Python SDK is open-source and released under the [MIT License](https://opensource.org/licenses/MIT).
