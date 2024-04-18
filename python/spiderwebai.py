import os
import requests


class SpiderWebAIApp:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("SPIDER_API_KEY")
        if self.api_key is None:
            raise ValueError("No API key provided")

    def scrape_url(self, url, params=None):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        json_data = {"url": url, "budget": '{"*":1}'}
        if params:
            json_data.update(params)
        response = self._post_request(
            "https://spider.a11ywatch.com/v1/crawl", json_data, headers, False
        )
        if response.status_code == 200:
            response = response.json()
            if response["success"] == True:
                return response["data"]
            else:
                raise Exception(f'Failed to scrape URL. Error: {response["error"]}')

        elif response.status_code in [402, 409, 500]:
            error_message = response.json().get("error", "Unknown error occurred")
            raise Exception(
                f"Failed to scrape URL. Status code: {response.status_code}. Error: {error_message}"
            )
        else:
            raise Exception(
                f"Failed to scrape URL. Status code: {response.status_code}"
            )

    def crawl_url(self, url, params=None, stream=False):
        headers = self._prepare_headers()
        json_data = {"url": url}
        if params:
            json_data.update(params)
        response = self._post_request(
            "https://spider.a11ywatch.com/v1/crawl", json_data, headers, stream
        )
        if stream:
            return response
        elif response.status_code == 200:
            return response.json()
        else:
            self._handle_error(response, "start crawl")

    def _prepare_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _post_request(self, url, data, headers, stream):
        return requests.post(url, headers=headers, json=data, stream=stream)

    def _get_request(self, url, headers):
        return requests.get(url, headers=headers)

    def _handle_error(self, response, action):
        if response.status_code in [402, 409, 500]:
            error_message = response.json().get("error", "Unknown error occurred")
            raise Exception(
                f"Failed to {action}. Status code: {response.status_code}. Error: {error_message}"
            )
        else:
            raise Exception(
                f"Unexpected error occurred while trying to {action}. Status code: {response.status_code}"
            )
