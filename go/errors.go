package spider

import "fmt"

// AIStudioSubscriptionRequired is returned when the API key does not
// have an active AI Studio subscription (HTTP 402).
type AIStudioSubscriptionRequired struct{}

func (e *AIStudioSubscriptionRequired) Error() string {
	return "AI Studio subscription required. Subscribe at https://spider.cloud/ai-studio"
}

// AIStudioRateLimitExceeded is returned when the AI Studio rate limit
// is exceeded server-side (HTTP 429).
type AIStudioRateLimitExceeded struct {
	RetryAfterMs int
}

func (e *AIStudioRateLimitExceeded) Error() string {
	return fmt.Sprintf("AI Studio rate limit exceeded. Retry after %dms", e.RetryAfterMs)
}

// APIError represents a non-OK HTTP response from the Spider API.
type APIError struct {
	StatusCode int
	Action     string
}

func (e *APIError) Error() string {
	return fmt.Sprintf("failed to %s: status code %d", e.Action, e.StatusCode)
}
