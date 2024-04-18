# SpiderWebAI Python SDK

The SpiderWebAI Python SDK offers a toolkit for straightforward website scraping, crawling at scale, and other utilities like extracting links and taking screenshots, enabling you to collect data formatted for compatibility with language models (LLMs). It features a user-friendly interface for seamless integration with the SpiderWebAI API.

## Installation

To install the SpiderWebAI Python SDK, you can use pip:

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
crawler_params = {
    'limit': 1,
    'proxy_enabled': True,
    'store_data': False,
    'metadata': False,
    'request': 'http'
}
crawl_result = app.crawl_url(crawl_url, params=crawler_params)
```

### Scraping a URL

To scrape data from a single URL:

```python
url = 'https://example.com'
scraped_data = app.scrape_url(url)
```

### Crawling a Website

To automate crawling a website:

```python
crawl_url = 'https://example.com'
crawl_params = {
    'limit': 200,
    'request': 'smart_mode'
}
crawl_result = app.crawl_url(crawl_url, params=crawl_params)
```

### Retrieving Links from a URL(s)

Extract all links from a specified URL:

```python
url = 'https://example.com'
links = app.links(url)
```

### Taking Screenshots of a URL(s)

Capture a screenshot of a given URL:

```python
url = 'https://example.com'
screenshot = app.screenshot(url)
```

### Extracting Contact Information

Extract contact details from a specified URL:

```python
url = 'https://example.com'
contacts = app.extract_contacts(url)
```

### Labeling Data from a URL(s)

Label the data extracted from a particular URL:

```python
url = 'https://example.com'
labeled_data = app.label(url)
```

### Checking Available Credits

You can check the remaining credits on your account:

```python
credits = app.get_credits()
```

## Error Handling

The SDK handles errors returned by the SpiderWebAI API and raises appropriate exceptions. If an error occurs during a request, an exception will be raised with a descriptive error message.

## Contributing

Contributions to the SpiderWebAI Python SDK are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## License

The SpiderWebAI Python SDK is open-source and released under the [MIT License](https://opensource.org/licenses/MIT).
