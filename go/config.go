package spider

// API configuration constants.
const (
	BaseURL    = "https://api.spider.cloud"
	APIVersion = "v1"
	Version    = "0.1.0"
)

// API routes.
const (
	RouteCrawl       = "crawl"
	RouteLinks       = "links"
	RouteScreenshot  = "screenshot"
	RouteSearch      = "search"
	RouteTransform   = "transform"
	RouteUnblocker   = "unblocker"
	RouteDataCredits = "data/credits"
	RouteData        = "data"
	RouteAICrawl     = "ai/crawl"
	RouteAIScrape    = "ai/scrape"
	RouteAISearch    = "ai/search"
	RouteAIBrowser   = "ai/browser"
	RouteAILinks     = "ai/links"
)

// RequestType controls the rendering method.
type RequestType string

const (
	RequestHTTP   RequestType = "http"
	RequestChrome RequestType = "chrome"
	RequestSmart  RequestType = "smart"
)

// ReturnFormat controls the output format.
type ReturnFormat string

const (
	FormatMarkdown   ReturnFormat = "markdown"
	FormatCommonmark ReturnFormat = "commonmark"
	FormatRaw        ReturnFormat = "raw"
	FormatText       ReturnFormat = "text"
	FormatHTML2Text  ReturnFormat = "html2text"
	FormatBytes      ReturnFormat = "bytes"
	FormatScreenshot ReturnFormat = "screenshot"
	FormatXML        ReturnFormat = "xml"
	FormatEmpty      ReturnFormat = "empty"
)

// ProxyType specifies which proxy pool to use.
type ProxyType string

const (
	ProxyResidential        ProxyType = "residential"
	ProxyMobile             ProxyType = "mobile"
	ProxyISP                ProxyType = "isp"
	ProxyResidentialFast    ProxyType = "residential_fast"
	ProxyResidentialStatic  ProxyType = "residential_static"
	ProxyResidentialPremium ProxyType = "residential_premium"
	ProxyResidentialCore    ProxyType = "residential_core"
	ProxyResidentialPlus    ProxyType = "residential_plus"
)

// Collection identifies a data table for the data endpoints.
type Collection string

const (
	CollectionWebsites      Collection = "websites"
	CollectionPages         Collection = "pages"
	CollectionPagesMetadata Collection = "pages_metadata"
	CollectionContacts      Collection = "contacts"
	CollectionCrawlState    Collection = "crawl_state"
	CollectionCrawlLogs     Collection = "crawl_logs"
	CollectionProfiles      Collection = "profiles"
	CollectionCredits       Collection = "credits"
	CollectionWebhooks      Collection = "webhooks"
	CollectionAPIKeys       Collection = "api_keys"
)

// AIStudioTier represents the AI Studio subscription level.
type AIStudioTier string

const (
	TierStarter  AIStudioTier = "starter"
	TierLite     AIStudioTier = "lite"
	TierStandard AIStudioTier = "standard"
	TierCustom   AIStudioTier = "custom"
)

// AIStudioRateLimits maps tiers to requests per second.
var AIStudioRateLimits = map[AIStudioTier]int{
	TierStarter:  1,
	TierLite:     5,
	TierStandard: 10,
	TierCustom:   25,
}

// SpiderParams are the core crawl/scrape request parameters.
// Fields use json:"snake_case" tags matching the API.
type SpiderParams struct {
	URL                string            `json:"url,omitempty"`
	Limit              int               `json:"limit,omitempty"`
	Depth              int               `json:"depth,omitempty"`
	Request            RequestType       `json:"request,omitempty"`
	ReturnFormat       ReturnFormat      `json:"return_format,omitempty"`
	TLD                bool              `json:"tld,omitempty"`
	Metadata           bool              `json:"metadata,omitempty"`
	Cache              bool              `json:"cache,omitempty"`
	Stealth            bool              `json:"stealth,omitempty"`
	Fingerprint        bool              `json:"fingerprint,omitempty"`
	Readability        bool              `json:"readability,omitempty"`
	Storageless        bool              `json:"storageless,omitempty"`
	Sitemap            bool              `json:"sitemap,omitempty"`
	SitemapOnly        bool              `json:"sitemap_only,omitempty"`
	ReturnPageLinks    bool              `json:"return_page_links,omitempty"`
	ReturnHeaders      bool              `json:"return_headers,omitempty"`
	ReturnCookies      bool              `json:"return_cookies,omitempty"`
	ReturnEmbeddings   bool              `json:"return_embeddings,omitempty"`
	FullResources      bool              `json:"full_resources,omitempty"`
	LiteMode           bool              `json:"lite_mode,omitempty"`
	DisableHints       bool              `json:"disable_hints,omitempty"`
	DisableIntercept   bool              `json:"disable_intercept,omitempty"`
	RunInBackground    bool              `json:"run_in_background,omitempty"`
	SkipConfigChecks   bool              `json:"skip_config_checks,omitempty"`
	RespectRobots      bool              `json:"respect_robots,omitempty"`
	Scroll             int               `json:"scroll,omitempty"`
	RequestTimeout     int               `json:"request_timeout,omitempty"`
	MaxCreditsPerPage  int               `json:"max_credits_per_page,omitempty"`
	Proxy              ProxyType         `json:"proxy,omitempty"`
	RemoteProxy        string            `json:"remote_proxy,omitempty"`
	CountryCode        string            `json:"country_code,omitempty"`
	Locale             string            `json:"locale,omitempty"`
	Encoding           string            `json:"encoding,omitempty"`
	UserAgent          string            `json:"user_agent,omitempty"`
	Cookies            string            `json:"cookies,omitempty"`
	RootSelector       string            `json:"root_selector,omitempty"`
	RedirectPolicy     string            `json:"redirect_policy,omitempty"`
	Blacklist          []string          `json:"blacklist,omitempty"`
	Whitelist          []string          `json:"whitelist,omitempty"`
	ExternalDomains    []string          `json:"external_domains,omitempty"`
	Headers            map[string]string `json:"headers,omitempty"`
	Budget             map[string]int    `json:"budget,omitempty"`
}

// SearchParams extends SpiderParams with search-specific fields.
type SearchParams struct {
	SpiderParams
	Search           string `json:"search,omitempty"`
	SearchLimit      int    `json:"search_limit,omitempty"`
	FetchPageContent *bool  `json:"fetch_page_content,omitempty"`
	Location         string `json:"location,omitempty"`
	Country          string `json:"country,omitempty"`
	Language         string `json:"language,omitempty"`
	Num              int    `json:"num,omitempty"`
	Page             int    `json:"page,omitempty"`
	WebsiteLimit     int    `json:"website_limit,omitempty"`
	QuickSearch      bool   `json:"quick_search,omitempty"`
}

// TransformParams are the request parameters for the transform endpoint.
type TransformParams struct {
	Data         []Resource   `json:"data"`
	ReturnFormat ReturnFormat `json:"return_format,omitempty"`
	Readability  bool         `json:"readability,omitempty"`
	Clean        bool         `json:"clean,omitempty"`
	CleanFull    bool         `json:"clean_full,omitempty"`
}

// Resource represents a single item for the transform endpoint.
type Resource struct {
	HTML    string `json:"html,omitempty"`
	Content string `json:"content,omitempty"`
	URL     string `json:"url,omitempty"`
	Lang    string `json:"lang,omitempty"`
}

// AIParams extends SpiderParams with a prompt for AI Studio endpoints.
type AIParams struct {
	SpiderParams
	Prompt string `json:"prompt,omitempty"`
}

// SpiderResponse is the standard per-page response from the API.
type SpiderResponse struct {
	Content string `json:"content,omitempty"`
	Message string `json:"message,omitempty"`
	Error   string `json:"error,omitempty"`
	Status  int    `json:"status,omitempty"`
	URL     string `json:"url,omitempty"`
}

// Credits represents the account credit balance response.
type Credits struct {
	Credits int `json:"credits"`
}
