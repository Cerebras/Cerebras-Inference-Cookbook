"""
Constants for hyper-personalization email generation.

This module contains all configuration constants including:
- Color schemes for different user preferences
- Product mappings by gender
- Language mappings
"""

# Color themes based on (preferred_color, background_mode)
# Each scheme defines colors for all email template elements
COLOR_SCHEMES = {
    ("red", "bright"): {
        "background_color": "#FFFFFF",
        "text_color": "#1F2937",
        "secondary_text_color": "#6B7280",
        "header_bg_color": "#FFFFFF",
        "hero_bg_color": "#FEE2E2",
        "headline_color": "#DC2626",
        "subheadline_color": "#374151",
        "cta_bg_color": "#DC2626",
        "cta_text_color": "#FFFFFF",
        "content_bg_color": "#FFFFFF",
        "promo_bg_color": "#DC2626",
        "promo_text_color": "#FFFFFF",
    },
    ("red", "dark"): {
        "background_color": "#1F2937",
        "text_color": "#F9FAFB",
        "secondary_text_color": "#D1D5DB",
        "header_bg_color": "#111827",
        "hero_bg_color": "#7F1D1D",
        "headline_color": "#FCA5A5",
        "subheadline_color": "#E5E7EB",
        "cta_bg_color": "#EF4444",
        "cta_text_color": "#FFFFFF",
        "content_bg_color": "#374151",
        "promo_bg_color": "#991B1B",
        "promo_text_color": "#FFFFFF",
    },
    ("green", "bright"): {
        "background_color": "#FFFFFF",
        "text_color": "#1F2937",
        "secondary_text_color": "#6B7280",
        "header_bg_color": "#FFFFFF",
        "hero_bg_color": "#D1FAE5",
        "headline_color": "#059669",
        "subheadline_color": "#374151",
        "cta_bg_color": "#059669",
        "cta_text_color": "#FFFFFF",
        "content_bg_color": "#FFFFFF",
        "promo_bg_color": "#059669",
        "promo_text_color": "#FFFFFF",
    },
    ("green", "dark"): {
        "background_color": "#1F2937",
        "text_color": "#F9FAFB",
        "secondary_text_color": "#D1D5DB",
        "header_bg_color": "#111827",
        "hero_bg_color": "#064E3B",
        "headline_color": "#6EE7B7",
        "subheadline_color": "#E5E7EB",
        "cta_bg_color": "#10B981",
        "cta_text_color": "#FFFFFF",
        "content_bg_color": "#374151",
        "promo_bg_color": "#047857",
        "promo_text_color": "#FFFFFF",
    },
    ("white", "bright"): {
        "background_color": "#FFFFFF",
        "text_color": "#1F2937",
        "secondary_text_color": "#6B7280",
        "header_bg_color": "#F9FAFB",
        "hero_bg_color": "#F3F4F6",
        "headline_color": "#111827",
        "subheadline_color": "#374151",
        "cta_bg_color": "#1F2937",
        "cta_text_color": "#FFFFFF",
        "content_bg_color": "#FFFFFF",
        "promo_bg_color": "#1F2937",
        "promo_text_color": "#FFFFFF",
    },
    ("white", "dark"): {
        "background_color": "#111827",
        "text_color": "#F9FAFB",
        "secondary_text_color": "#D1D5DB",
        "header_bg_color": "#1F2937",
        "hero_bg_color": "#374151",
        "headline_color": "#FFFFFF",
        "subheadline_color": "#E5E7EB",
        "cta_bg_color": "#F9FAFB",
        "cta_text_color": "#111827",
        "content_bg_color": "#1F2937",
        "promo_bg_color": "#374151",
        "promo_text_color": "#FFFFFF",
    },
}

# Product names by gender
PRODUCT_NAMES = {
    "male": "Patagonia Fitz Roy Icon Responsibili-Tee - Men's",
    "female": "Patagonia Classic Microdini Jacket - Women's"
}

# Product images by gender and color preference
PRODUCT_IMAGES = {
    "male": {
        "red": "sample-data/male-red.jpg",
        "green": "sample-data/male-green.jpg",
        "white": "sample-data/male-white.jpg",
    },
    "female": {
        "red": "sample-data/women-red-jacket.jpg",
        "green": "sample-data/women-grey-jacket.jpg",
        "white": "sample-data/women-white-jacket.jpg",
    }
}

# Language code to full name mapping
LANGUAGE_MAP = {
    "en": "English",
    "sp": "Spanish", 
    "de": "German"
}

# Cerebras model to use
MODEL = "gpt-oss-120b"

# Personality-based tone guidance for prompts
PERSONALITY_GUIDANCE = {
    "extroverted": "Use energetic, enthusiastic language with exclamation points. Be bold and exciting.",
    "introverted": "Use calm, thoughtful language. Be understated and refined. Avoid excessive enthusiasm.",
    "balanced": "Use warm, approachable language. Be friendly but not over-the-top."
}

# Communication tone guidance for prompts
TONE_GUIDANCE = {
    "formal": "Use professional, polished language. Avoid slang or casual expressions.",
    "casual": "Use relaxed, conversational language. Feel free to use contractions.",
    "friendly": "Use warm, personable language. Be welcoming and approachable."
}
