use bytes::Bytes;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Deserialize, Serialize)]
#[serde(untagged)]
pub enum Content {
    /// A raw string (e.g. plain text or HTML).
    String(String),
    /// Raw binary bytes.
    Bytes(Bytes),
    /// Structured object with optional formats.
    Object {
        raw: Option<String>,
        bytes: Option<Bytes>,
        text: Option<String>,
        markdown: Option<String>,
        html2text: Option<String>,
        screenshot: Option<Bytes>,
    },
}

impl Content {
    /// Return the best-guess string representation of the content.
    pub fn as_str(&self) -> Option<&str> {
        match self {
            Content::String(s) => Some(s),
            Content::Object { text: Some(t), .. } => Some(t),
            Content::Object { raw: Some(r), .. } => Some(r),
            Content::Object {
                html2text: Some(h), ..
            } => Some(h),
            Content::Object {
                markdown: Some(m), ..
            } => Some(m),
            _ => None,
        }
    }

    /// Return raw bytes if available.
    pub fn as_bytes(&self) -> Option<&Bytes> {
        match self {
            Content::Bytes(b) => Some(b),
            Content::Object { bytes: Some(b), .. } => Some(b),
            Content::Object {
                screenshot: Some(b),
                ..
            } => Some(b),
            _ => None,
        }
    }

    /// Return text content or a fallback string view of bytes if UTF-8.
    pub fn as_utf8_lossy(&self) -> Option<String> {
        match self {
            Content::String(s) => Some(s.clone()),
            Content::Object { text: Some(t), .. } => Some(t.clone()),
            Content::Object { raw: Some(r), .. } => Some(r.clone()),
            Content::Object {
                markdown: Some(m), ..
            } => Some(m.clone()),
            Content::Object {
                html2text: Some(h), ..
            } => Some(h.clone()),
            Content::Bytes(b) => Some(String::from_utf8_lossy(b).to_string()),
            Content::Object { bytes: Some(b), .. } => Some(String::from_utf8_lossy(b).to_string()),
            _ => None,
        }
    }

    /// Return the full object if the content is structured.
    pub fn as_object(&self) -> Option<&Self> {
        match self {
            Content::Object { .. } => Some(self),
            _ => None,
        }
    }

    /// Check if the content is a screenshot (binary).
    pub fn has_screenshot(&self) -> bool {
        matches!(
            self,
            Content::Object {
                screenshot: Some(_),
                ..
            }
        )
    }

    /// Check if the content is empty or contains only whitespace.
    pub fn is_empty(&self) -> bool {
        match self {
            Content::String(s) => s.trim().is_empty(),
            Content::Bytes(b) => b.is_empty(),
            Content::Object {
                raw,
                text,
                markdown,
                html2text,
                bytes,
                screenshot,
            } => {
                raw.as_ref().map_or(true, |s| s.trim().is_empty())
                    && text.as_ref().map_or(true, |s| s.trim().is_empty())
                    && markdown.as_ref().map_or(true, |s| s.trim().is_empty())
                    && html2text.as_ref().map_or(true, |s| s.trim().is_empty())
                    && bytes.as_ref().map_or(true, |b| b.is_empty())
                    && screenshot.as_ref().map_or(true, |b| b.is_empty())
            }
        }
    }

    /// Try to extract a plain `.html` or `.txt` suitable string.
    pub fn extract_plaintext(&self) -> Option<String> {
        self.as_str()
            .map(|s| s.to_string())
            .or_else(|| self.as_utf8_lossy())
    }

    /// Returns all the content keys available.
    pub fn available_keys(&self) -> Vec<&'static str> {
        match self {
            Content::Object {
                raw,
                bytes,
                text,
                markdown,
                html2text,
                screenshot,
            } => {
                let mut keys = vec![];
                if raw.is_some() {
                    keys.push("raw");
                }
                if bytes.is_some() {
                    keys.push("bytes");
                }
                if text.is_some() {
                    keys.push("text");
                }
                if markdown.is_some() {
                    keys.push("markdown");
                }
                if html2text.is_some() {
                    keys.push("html2text");
                }
                if screenshot.is_some() {
                    keys.push("screenshot");
                }
                keys
            }
            Content::String(_) => vec!["string"],
            Content::Bytes(_) => vec!["bytes"],
        }
    }
}

#[derive(Debug, Deserialize, Serialize, Default)]
pub struct ApiResponse {
    /// Textual or binary content of the page.
    pub content: Bytes,
    /// Status code returned from the source.
    pub status: u16,
    /// Final URL requested.
    pub url: String,
    /// All links found on the page.
    pub links: Option<Vec<String>>,
    /// Optional request map with timing values.
    pub request_map: Option<HashMap<String, f64>>,
    /// Optional metadata associated with the page.
    pub metadata: Option<Metadata>,
    /// Optional request cost breakdown.
    pub costs: Option<Costs>,
    /// Optional error message.
    pub error: Option<String>,
}

#[derive(Debug, Deserialize, Serialize, Default)]
pub struct Costs {
    /// The cost of the AI.
    pub ai_cost: f64,
    /// The cost of the bytes transferred.
    pub bytes_transferred_cost: f64,
    /// The cost of the compute.
    pub compute_cost: f64,
    /// The cost of the file.
    pub file_cost: f64,
    /// The total cost of the request.
    pub total_cost: f64,
    /// The cost of the transform.
    pub transform_cost: f64,
}

#[derive(Debug, Deserialize, Serialize, Default)]
pub struct Metadata {
    /// SEO title of the page.
    pub title: String,
    /// Meta description of the page.
    pub description: String,
    /// Final resolved URL if available.
    pub url: Option<String>,
    /// Social Open Graph preview image.
    #[serde(rename = "og_image")]
    pub image: Option<String>,
    /// Optional keywords extracted from content.
    pub keywords: Option<Vec<String>>,
    /// Optional raw YouTube transcript string.
    pub yt_transcript: Option<String>,
    /// Domain of the source page.
    pub domain: Option<String>,
    /// Additional fallback fields.
    pub pathname: Option<String>,
    pub original_url: Option<String>,
    pub user_id: Option<String>,
    /// File-type classification if detected.
    pub resource_type: Option<String>,
    /// File size in bytes if known.
    pub file_size: Option<u64>,
    /// Any structured extraction result (generic).
    pub extracted_data: Option<serde_json::Value>,
    /// automation metadata:
    pub automation_data: Option<serde_json::Value>
}

#[derive(Debug, Deserialize, Serialize, Default)]
pub struct SearchList {
    /// The main content list.
    pub content: Vec<SearchEntry>,
}

#[derive(Debug, Deserialize, Serialize, Default)]
pub struct SearchEntry {
    #[serde(default)]
    /// The search description.
    pub description: Option<String>,
    #[serde(default)]
    /// The search title.
    pub title: Option<String>,
    #[serde(default)]
    /// The search url.
    pub url: String,
}
