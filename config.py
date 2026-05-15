"""
Configuration settings for Culinary Trend MCP Server
"""

import os
from pathlib import Path
from datetime import timedelta

# ============================================================================
# SEARXNG CONFIGURATION
# ============================================================================

# SearXNG endpoint URL
SEARXNG_URL = os.getenv("SEARXNG_URL", "http://localhost:8090")

# Request timeout in seconds
SEARXNG_TIMEOUT = int(os.getenv("SEARXNG_TIMEOUT", "30"))

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Database file location
DATABASE_PATH = os.getenv("DATABASE_PATH", "culinary_trends.db")
DATABASE_TIMEOUT = 10

# ============================================================================
# MONITORING CONFIGURATION
# ============================================================================

# Default monitoring check interval (in minutes)
DEFAULT_CHECK_INTERVAL = 30

# Minimum check interval allowed (in minutes)
MIN_CHECK_INTERVAL = 5

# Maximum check interval allowed (in minutes)
MAX_CHECK_INTERVAL = 1440  # 24 hours

# How long to keep historical data (in days)
MONITORING_RETENTION_DAYS = 30

# ============================================================================
# SEARCH CONFIGURATION
# ============================================================================

# Default number of search results
DEFAULT_RESULT_LIMIT = 10

# Maximum number of search results
MAX_RESULT_LIMIT = 50

# Culinary search keywords for trend detection
CULINARY_KEYWORDS = [
    "viral food",
    "trending recipes",
    "food trends",
    "trending desserts",
    "trending bread",
    "trending pastry",
    "new cooking techniques",
    "food viral",
    "recipe trending",
    "popular food",
    "food challenge",
]

# Social media platforms to monitor
SOCIAL_PLATFORMS = {
    "tiktok": "site:tiktok.com",
    "instagram": "site:instagram.com",
    "pinterest": "site:pinterest.com",
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "culinary_trends.log")

# ============================================================================
# MCP SERVER CONFIGURATION
# ============================================================================

# Server name and version
SERVER_NAME = "culinary-trend-mcp"
SERVER_VERSION = "1.0.0"

# Server stdio mode (for MCP protocol)
USE_STDIO = True
