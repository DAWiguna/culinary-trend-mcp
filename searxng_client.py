"""
SearXNG API Client
Handles all communication with local SearXNG instance
"""

import requests
import logging
import config
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class SearXNGClient:
    """Client for SearXNG API"""

    def __init__(self):
        self.base_url = config.SEARXNG_URL
        self.timeout = config.SEARXNG_TIMEOUT
        logger.info(f"SearXNG Client initialized with URL: {self.base_url}")

    def health_check(self) -> bool:
        """Check if SearXNG is running"""
        try:
            response = requests.get(
                f"{self.base_url}/",
                timeout=self.timeout
            )
            is_healthy = response.status_code == 200
            if is_healthy:
                logger.info("SearXNG health check passed")
            else:
                logger.warning(f"SearXNG returned status {response.status_code}")
            return is_healthy
        except Exception as e:
            logger.error(f"SearXNG health check failed: {e}")
            return False

    def search_web(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search general web content"""
        try:
            params = {
                "q": query,
                "format": "json",
                "pageno": 1,
            }

            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                results = []

                for result in data.get("results", [])[:limit]:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("content", ""),
                        "source": "web",
                    })

                logger.info(f"Web search found {len(results)} results for: {query}")
                return results
            else:
                logger.error(f"SearXNG returned status {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error searching web: {e}")
            return []

    def search_news(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search news content"""
        try:
            params = {
                "q": query,
                "format": "json",
                "category": "news",
            }

            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                results = []

                for result in data.get("results", [])[:limit]:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("content", ""),
                        "source": "news",
                    })

                logger.info(f"News search found {len(results)} results for: {query}")
                return results
            else:
                return []

        except Exception as e:
            logger.error(f"Error searching news: {e}")
            return []

    def search_social_media(self, query: str, platforms: str = "all", limit: int = 10) -> List[Dict[str, Any]]:
        """Search social media platforms"""
        try:
            results = []

            if platforms == "all":
                platform_list = ["tiktok", "instagram", "pinterest"]
            else:
                platform_list = [platforms] if platforms in config.SOCIAL_PLATFORMS else ["all"]

            for platform in platform_list:
                platform_query = f"{query} {config.SOCIAL_PLATFORMS.get(platform, '')}"

                params = {
                    "q": platform_query,
                    "format": "json",
                }

                response = requests.get(
                    f"{self.base_url}/search",
                    params=params,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    data = response.json()

                    for result in data.get("results", [])[:limit]:
                        results.append({
                            "title": result.get("title", ""),
                            "url": result.get("url", ""),
                            "snippet": result.get("content", ""),
                            "platform": platform,
                            "source": "social_media",
                        })

            logger.info(f"Social media search found {len(results)} results for: {query}")
            return results

        except Exception as e:
            logger.error(f"Error searching social media: {e}")
            return []

    def search_images(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for images"""
        try:
            params = {
                "q": query,
                "format": "json",
                "category": "images",
            }

            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                results = []

                for result in data.get("results", [])[:limit]:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "image_url": result.get("img_src", ""),
                        "source": "images",
                    })

                return results
            else:
                return []

        except Exception as e:
            logger.error(f"Error searching images: {e}")
            return []
