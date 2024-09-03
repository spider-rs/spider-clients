# Scrape

We will assume that you have installed the Spider package and exported your API key as an environment variable. If you haven't, please refer to the [Getting Started](./getting-started.md) guide.

Scrape a website and return the content.

```python
from spider import Spider

app = Spider()
url = 'https://spider.cloud'
scraped_data = app.scrape_url(url)

print(scraped_data)
```

The `scrape_url` method returns the content of the website in markdown format as default. Next we will see how to scrape with with different parameters.

## Scrape with different parameters

The `scrape_url` method has the following parameters:

- `url` (str): The URL of the website to scrape.

the following are optional parameters and can be set in the `params` dictionary:

- `request` ("http", "chrome", "smart") : The type of request to make. Default is "http".
- `return_format` ("raw", "markdown", "commonmark", "html2text", "text", "bytes") : The format in which to return the scraped data. Default is "markdown".
- `stealth`, `anti_bot` and a ton of other parameters that you can find in the [documentation](https://spider.cloud/docs/api?ref=python-sdk-book).

```python
from spider import Spider

app = Spider()
url = "https://spider.cloud"
scraped_data = app.scrape_url(url, params={"request_timeout": 10, "stealth": True})

print(scraped_data)
```

If you have a lot of params, setting them inside the `scrape_url` method can be cumbersome. You can set them in a seperate `params` variable that has the `RequestParams` type which is also available in the `spider` package.

```python
from spider import Spider, spider_types

params: spider_types.RequestParamsDict = {
    "request_timeout": 10,
    "stealth": True,
    # Easier to read and intellisense will help you with the available options
}

app = Spider()
url = "https://spider.cloud"
scraped_data = app.scrape_url(url, params)

print(scraped_data)
```
