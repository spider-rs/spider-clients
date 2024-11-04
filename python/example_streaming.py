
from spider import Spider

# Initialize the Spider with your API key using the env key SPIDER_API_KEY
app = Spider()

crawler_params = {
    'limit': 1000,
    'proxy_enabled': False,
    'store_data': False,
    'metadata': False,
    'request': 'http'
}

count = [0]

def process_json(data: dict) -> None:
    print(f"Processing: {count[0]}")
    count[0] += 1
    for key, value in data.items():
        print(f"{key}: {value}")

app.crawl_url('https://spider.cloud', params=crawler_params, stream=True, callback=process_json)
