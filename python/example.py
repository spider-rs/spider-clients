import asyncio
from spider import Spider, AsyncSpider

# Initialize the Spider with your API key using the env key SPIDER_API_KEY
app = Spider()
async_app = AsyncSpider()

crawler_params = {
    'limit': 5,
    'proxy_enabled': True,
    'store_data': False,
    'metadata': False,
    'request': 'http'
}
crawl_result = app.crawl_url('https://spider.cloud', params=crawler_params)
async_crawl_result = asyncio.run(app.crawl_url('https://spider.cloud', params=crawler_params))

print(crawl_result)



