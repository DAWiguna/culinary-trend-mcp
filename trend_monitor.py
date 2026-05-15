"""
Trend Monitoring Engine
Handles continuous monitoring and pattern detection
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
from database import TrendDatabase
from searxng_client import SearXNGClient
import config

logger = logging.getLogger(__name__)


class TrendMonitor:
    """Monitors culinary trends"""

    def __init__(self):
        self.db = TrendDatabase()
        self.searxng = SearXNGClient()
        self.active_monitors = {}
        logger.info("Trend Monitor initialized")

    def start_monitoring(self, trend_name: str, query: str, platforms: str = "all",
                        check_interval_minutes: int = 30, notes: str = "") -> str:
        """Start monitoring a trend"""
        try:
            # Generate unique monitoring ID
            monitoring_id = str(uuid.uuid4())

            # Validate interval
            if check_interval_minutes < config.MIN_CHECK_INTERVAL:
                check_interval_minutes = config.MIN_CHECK_INTERVAL
            elif check_interval_minutes > config.MAX_CHECK_INTERVAL:
                check_interval_minutes = config.MAX_CHECK_INTERVAL

            # Add to database
            self.db.add_monitor(
                monitoring_id=monitoring_id,
                trend_name=trend_name,
                query=query,
                platforms=platforms,
                notes=notes
            )

            # Store in active monitors
            self.active_monitors[monitoring_id] = {
                "trend_name": trend_name,
                "query": query,
                "platforms": platforms,
                "interval": check_interval_minutes,
            }

            # Perform initial search
            self._perform_search(monitoring_id, query, platforms)

            logger.info(f"Started monitoring: {trend_name} (ID: {monitoring_id})")
            return monitoring_id

        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            raise

    def stop_monitoring(self, monitoring_id: str) -> bool:
        """Stop monitoring a trend"""
        try:
            if monitoring_id in self.active_monitors:
                del self.active_monitors[monitoring_id]

            self.db.update_monitor_status(monitoring_id, "stopped")
            logger.info(f"Stopped monitoring: {monitoring_id}")
            return True

        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
            return False

    def get_active_monitors(self) -> List[Dict[str, Any]]:
        """Get list of active monitors"""
        try:
            return self.active_monitors
        except Exception as e:
            logger.error(f"Error getting active monitors: {e}")
            return []

    def get_trend_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        try:
            return self.db.get_recent_alerts(limit=limit)
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []

    def get_trend_history(self, trend_name: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get trend history"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            return self.db.get_trend_history(trend_name, cutoff_date)
        except Exception as e:
            logger.error(f"Error getting trend history: {e}")
            return []

    def detect_trending_patterns(self, trend_name: str) -> Dict[str, Any]:
        """Detect emerging patterns in a trend"""
        try:
            history = self.get_trend_history(trend_name, days=14)

            # Analyze patterns
            patterns = {
                "total_items": len(history),
                "trend_velocity": self._calculate_velocity(history),
                "emerging_sources": self._identify_sources(history),
                "platform_distribution": self._get_platform_distribution(history),
            }

            return patterns

        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return {}

    def _perform_search(self, monitoring_id: str, query: str, platforms: str):
        """Perform search and store results"""
        try:
            all_results = []

            # Search based on platform
            if platforms == "all" or platforms == "web":
                web_results = self.searxng.search_web(query)
                all_results.extend(web_results)

            if platforms == "all" or platforms in ["social", "tiktok", "instagram", "pinterest"]:
                social_results = self.searxng.search_social_media(query, platforms)
                all_results.extend(social_results)

            # Store results
            if all_results:
                self.db.store_monitoring_results(monitoring_id, all_results)
                self.db.create_alert(
                    monitoring_id,
                    "search_completed",
                    f"Found {len(all_results)} results",
                    len(all_results)
                )

        except Exception as e:
            logger.error(f"Error performing search: {e}")

    def _calculate_velocity(self, history: List[Dict[str, Any]]) -> str:
        """Calculate how fast trend is growing"""
        if not history:
            return "unknown"

        # Simple velocity calculation based on recent items
        recent = len([h for h in history if self._is_recent(h.get("search_date"))])
        total = len(history)

        if recent > total * 0.7:
            return "rapidly_growing"
        elif recent > total * 0.4:
            return "growing"
        else:
            return "stable"

    def _identify_sources(self, history: List[Dict[str, Any]]) -> List[str]:
        """Identify content sources"""
        sources = set()
        for item in history:
            if "source" in item:
                sources.add(item["source"])
        return list(sources)

    def _get_platform_distribution(self, history: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution across platforms"""
        platforms = {}
        for item in history:
            platform = item.get("platform", "unknown")
            platforms[platform] = platforms.get(platform, 0) + 1
        return platforms

    def _is_recent(self, date_str: str, days: int = 3) -> bool:
        """Check if date is recent"""
        try:
            if not date_str:
                return False
            date = datetime.fromisoformat(date_str)
            cutoff = datetime.now() - timedelta(days=days)
            return date > cutoff
        except:
            return False

    def cleanup(self):
        """Cleanup resources"""
        try:
            self.db.cleanup_old_data()
            self.db.close()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
