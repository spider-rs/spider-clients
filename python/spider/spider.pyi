from typing import TypedDict, Optional, Dict, List, Literal, Any


class RequestParamsDict(TypedDict, total=False):
    url: Optional[str]
    request: Optional[Literal["http", "chrome", "smart"]]
    limit: Optional[int]
    return_format: Optional[Literal["raw", "markdown", "html2text", "text", "bytes"]]
    tld: Optional[bool]
    depth: Optional[int]
    cache: Optional[bool]
    budget: Optional[Dict[str, int]]
    locale: Optional[str]
    cookies: Optional[str]
    stealth: Optional[bool]
    headers: Optional[Dict[str, str]]
    anti_bot: Optional[bool]
    metadata: Optional[bool]
    viewport: Optional[Dict[str, int]]
    encoding: Optional[str]
    subdomains: Optional[bool]
    user_agent: Optional[str]
    store_data: Optional[bool]
    gpt_config: Optional[List[str]]
    fingerprint: Optional[bool]
    storageless: Optional[bool]
    readability: Optional[bool]
    proxy_enabled: Optional[bool]
    respect_robots: Optional[bool]
    query_selector: Optional[str]
    full_resources: Optional[bool]
    request_timeout: Optional[int]
    run_in_background: Optional[bool]
    skip_config_checks: Optional[bool]


class Spider:
    api_key: str

    def __init__(self, api_key: Optional[str] = None) -> None: ...

    def api_post(
        self,
        endpoint: str,
        data: dict,
        stream: bool,
        content_type: str = "application/json",
    ) -> Any: ...

    def api_get(
        self, endpoint: str, stream: bool, content_type: str = "application/json"
    ) -> Any: ...

    def api_delete(
        self, endpoint: str, stream: bool, content_type: str = "application/json"
    ) -> Any: ...

    def scrape_url(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
    ) -> Any: ...

    def crawl_url(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
    ) -> Any: ...

    def links(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
    ) -> Any: ...

    def screenshot(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
    ) -> Any: ...

    def search(
        self,
        q: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
    ) -> Any: ...

    def transform(
        self, data: Any, params: Optional[RequestParamsDict] = None, stream: bool = False, content_type: str = "application/json"
    ) -> Any: ...

    def extract_contacts(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
    ) -> Any: ...

    def label(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
    ) -> Any: ...

    def get_crawl_state(
        self,
        url: str,
        params: Optional[RequestParamsDict] = None,
        stream: bool = False,
        content_type: str = "application/json",
    ) -> Any: ...

    def get_credits(self) -> Any: ...

    def data_post(self, table: str, data: Optional[RequestParamsDict] = None) -> Any: ...

    def data_get(
        self,
        table: str,
        params: Optional[RequestParamsDict] = None,
    ) -> Any: ...

    def data_delete(
        self,
        table: str,
        params: Optional[RequestParamsDict] = None,
    ) -> Any: ...

    def _prepare_headers(self, content_type: str = "application/json") -> Dict[str, str]: ...

    def _post_request(self, url: str, data: Any, headers: Dict[str, str], stream: bool = False) -> Any: ...

    def _get_request(self, url: str, headers: Dict[str, str], stream: bool = False) -> Any: ...

    def _delete_request(self, url: str, headers: Dict[str, str], stream: bool = False) -> Any: ...

    def _handle_error(self, response: Any, action: str) -> None: ...

