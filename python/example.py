from spiderwebai import SpiderWebAIApp

# Initialize the SpiderWebAIApp with your API key using the env key SPIDER_API_KEY
app = SpiderWebAIApp()

crawler_params = {
    'limit': 5,
    'proxy_enabled': True,
    'store_data': False,
    'metadata': False,
    'request': 'http'
}
crawl_result = app.crawl_url('https://spiderwebai.xyz', params=crawler_params)

print(crawl_result)