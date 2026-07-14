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

// UnlimitedPlanRequired is returned when the API key does not have an
// active Unlimited subscription (HTTP 403 with error code
// "unlimited_plan_required" or "unlimited_plan_inactive").
type UnlimitedPlanRequired struct {
	// Reason is the API error code: "unlimited_plan_required" or
	// "unlimited_plan_inactive".
	Reason string
}

func (e *UnlimitedPlanRequired) Error() string {
	if e.Reason == "unlimited_plan_inactive" {
		return "Unlimited plan inactive. Reactivate at https://spider.cloud/pricing?plan=unlimited"
	}
	return "Unlimited plan required. Subscribe at https://spider.cloud/pricing?plan=unlimited"
}

// UnlimitedConcurrencyLimitReached is returned when all purchased
// Unlimited concurrency seats are in flight (HTTP 429). Requests are
// not queued server-side; retry with backoff after RetryAfterMs.
type UnlimitedConcurrencyLimitReached struct {
	// Seats is the purchased concurrency limit (X-Concurrency-Limit header).
	Seats int
	// Active is the number of requests in flight (X-Concurrency-Active header).
	Active int
	// RetryAfterMs is the suggested wait from the Retry-After header.
	RetryAfterMs int
}

func (e *UnlimitedConcurrencyLimitReached) Error() string {
	return fmt.Sprintf("Unlimited concurrency limit reached (%d/%d seats in flight). Retry after %dms", e.Active, e.Seats, e.RetryAfterMs)
}

// APIError represents a non-OK HTTP response from the Spider API.
type APIError struct {
	StatusCode int
	Action     string
}

func (e *APIError) Error() string {
	return fmt.Sprintf("failed to %s: status code %d", e.Action, e.StatusCode)
}
