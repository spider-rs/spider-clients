import asyncio
from spider import AsyncSpider

# Initialize the AsyncSpider with your API key using the env key SPIDER_API_KEY
async_app = AsyncSpider()

crawler_params = {
    'limit': 5,
    'proxy_enabled': True,
    'store_data': False,
    'metadata': False,
    'request': 'http'
}

async_crawl_result = asyncio.run(async_app.crawl_url('https://spider.cloud', params=crawler_params))

print(async_crawl_result)