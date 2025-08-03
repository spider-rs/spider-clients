
from spider import Spider

# Initialize the Spider with your API key using the env key SPIDER_API_KEY
app = Spider()

crawler_params = {
    'limit': 5,
    'proxy_enabled': False,
    'metadata': False,
    'request': 'http'
}
crawl_result = app.crawl_url('https://spider.cloud', params=crawler_params)

print(crawl_result)