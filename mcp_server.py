"""
Culinary Trend MCP Server
Main server implementation for Model Context Protocol integration with Hermes
"""

import json
import logging
import sys
from typing import Dict, Any, List
import config
from searxng_client import SearXNGClient
from trend_monitor import TrendMonitor

# Setup logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(sys.stderr),
    ],
)

logger = logging.getLogger(__name__)


class CulinaryTrendMCPServer:
    """MCP Server for Culinary Trend Monitoring"""

    def __init__(self):
        self.searxng = SearXNGClient()
        self.monitor = TrendMonitor()
        logger.info("Culinary Trend MCP Server initialized")

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        try:
            method = request.get("method")
            params = request.get("params", {})

            logger.info(f"Handling request: {method}")

            # Route to appropriate handler
            if method == "search_trending_food":
                return self.search_trending_food(params)
            elif method == "search_social_media":
                return self.search_social_media(params)
            elif method == "start_monitoring_trend":
                return self.start_monitoring_trend(params)
            elif method == "stop_monitoring_trend":
                return self.stop_monitoring_trend(params)
            elif method == "get_active_monitors":
                return self.get_active_monitors(params)
            elif method == "get_trend_alerts":
                return self.get_trend_alerts(params)
            elif method == "get_monitoring_history":
                return self.get_monitoring_history(params)
            elif method == "detect_patterns":
                return self.detect_patterns(params)
            else:
                return {"error": f"Unknown method: {method}"}

        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {"error": str(e)}

    def search_trending_food(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for trending culinary content"""
        try:
            query = params.get("query", "")
            limit = params.get("limit", config.DEFAULT_RESULT_LIMIT)

            if not query:
                return {"error": "query parameter is required"}

            logger.info(f"Searching trending food: {query}")

            web_results = self.searxng.search_web(query, limit=limit // 2)
            news_results = self.searxng.search_news(query, limit=limit // 2)

            results = web_results + news_results

            return {
                "success": True,
                "query": query,
                "results_count": len(results),
                "results": results[:limit],
            }

        except Exception as e:
            logger.error(f"Error searching trending food: {e}")
            return {"error": str(e)}

    def search_social_media(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search social media platforms for food trends"""
        try:
            query = params.get("query", "")
            platforms = params.get("platforms", "all")
            limit = params.get("limit", config.DEFAULT_RESULT_LIMIT)

            if not query:
                return {"error": "query parameter is required"}

            logger.info(f"Searching social media: {query} on {platforms}")

            results = self.searxng.search_social_media(
                query=query, platforms=platforms, limit=limit
            )

            return {
                "success": True,
                "query": query,
                "platforms": platforms,
                "results_count": len(results),
                "results": results,
            }

        except Exception as e:
            logger.error(f"Error searching social media: {e}")
            return {"error": str(e)}

    def start_monitoring_trend(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start monitoring a culinary trend"""
        try:
            trend_name = params.get("trend_name", "")

            if not trend_name:
                return {"error": "trend_name parameter is required"}

            query = params.get("query", trend_name)
            platforms = params.get("platforms", "all")
            check_interval = params.get("check_interval_minutes", config.DEFAULT_CHECK_INTERVAL)
            notes = params.get("notes", "")

            monitoring_id = self.monitor.start_monitoring(
                trend_name=trend_name,
                query=query,
                platforms=platforms,
                check_interval_minutes=check_interval,
                notes=notes,
            )

            logger.info(f"Started monitoring trend: {trend_name} (ID: {monitoring_id})")

            return {
                "success": True,
                "monitoring_id": monitoring_id,
                "trend_name": trend_name,
                "platforms": platforms,
                "check_interval_minutes": check_interval,
                "message": f"Now monitoring '{trend_name}' every {check_interval} minutes",
            }

        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            return {"error": str(e)}

    def stop_monitoring_trend(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Stop monitoring a trend"""
        try:
            monitoring_id = params.get("monitoring_id", "")

            if not monitoring_id:
                return {"error": "monitoring_id parameter is required"}

            success = self.monitor.stop_monitoring(monitoring_id)

            if success:
                return {
                    "success": True,
                    "monitoring_id": monitoring_id,
                    "message": "Monitoring stopped",
                }
            else:
                return {"error": "Failed to stop monitoring"}

        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
            return {"error": str(e)}

    def get_active_monitors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of active monitoring tasks"""
        try:
            monitors = self.monitor.get_active_monitors()

            return {
                "success": True,
                "active_monitors_count": len(monitors),
                "monitors": monitors,
            }

        except Exception as e:
            logger.error(f"Error getting active monitors: {e}")
            return {"error": str(e)}

    def get_trend_alerts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get recent trend alerts and changes"""
        try:
            limit = params.get("limit", 20)
            alerts = self.monitor.get_trend_alerts(limit=limit)

            return {
                "success": True,
                "alerts_count": len(alerts),
                "alerts": alerts,
            }

        except Exception as e:
            logger.error(f"Error getting trend alerts: {e}")
            return {"error": str(e)}

    def get_monitoring_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get historical data for a monitored trend"""
        try:
            trend_name = params.get("trend_name", "")
            days = params.get("days", 7)

            if not trend_name:
                return {"error": "trend_name parameter is required"}

            history = self.monitor.get_trend_history(trend_name, days=days)

            return {
                "success": True,
                "trend_name": trend_name,
                "days": days,
                "results_count": len(history),
                "history": history,
            }

        except Exception as e:
            logger.error(f"Error getting monitoring history: {e}")
            return {"error": str(e)}

    def detect_patterns(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Detect emerging patterns in a trend"""
        try:
            trend_name = params.get("trend_name", "")

            if not trend_name:
                return {"error": "trend_name parameter is required"}

            patterns = self.monitor.detect_trending_patterns(trend_name)

            return {
                "success": True,
                "trend_name": trend_name,
                "patterns": patterns,
            }

        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return {"error": str(e)}

    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of available tools for MCP protocol"""
        return [
            {
                "name": "search_trending_food",
                "description": "Search for trending culinary content across web and news",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "What to search for (e.g., 'viral bread recipes')",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of results (default: 10)",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "search_social_media",
                "description": "Search social media for trending food content",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "What to search for",
                        },
                        "platforms": {
                            "type": "string",
                            "enum": ["all", "tiktok", "instagram", "pinterest"],
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of results (default: 10)",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "start_monitoring_trend",
                "description": "Start monitoring a culinary trend",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "trend_name": {
                            "type": "string",
                            "description": "Name of trend to monitor",
                        },
                        "query": {
                            "type": "string",
                            "description": "Custom search query (optional)",
                        },
                        "platforms": {
                            "type": "string",
                            "enum": ["all", "web", "social", "tiktok", "instagram", "pinterest"],
                        },
                        "check_interval_minutes": {
                            "type": "integer",
                            "description": "Check interval in minutes (default: 30)",
                        },
                    },
                    "required": ["trend_name"],
                },
            },
            {
                "name": "stop_monitoring_trend",
                "description": "Stop monitoring a trend",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "monitoring_id": {
                            "type": "string",
                            "description": "ID of monitoring task",
                        },
                    },
                    "required": ["monitoring_id"],
                },
            },
            {
                "name": "get_active_monitors",
                "description": "Get list of active monitors",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "get_trend_alerts",
                "description": "Get recent trend alerts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of alerts (default: 20)",
                        },
                    },
                },
            },
            {
                "name": "get_monitoring_history",
                "description": "Get historical trend data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "trend_name": {
                            "type": "string",
                            "description": "Trend name",
                        },
                        "days": {
                            "type": "integer",
                            "description": "Days to look back (default: 7)",
                        },
                    },
                    "required": ["trend_name"],
                },
            },
            {
                "name": "detect_patterns",
                "description": "Analyze emerging patterns",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "trend_name": {
                            "type": "string",
                            "description": "Trend name",
                        },
                    },
                    "required": ["trend_name"],
                },
            },
        ]

    def run(self):
        """Run the MCP server"""
        try:
            logger.info("Starting Culinary Trend MCP Server")
            logger.info(f"SearXNG endpoint: {config.SEARXNG_URL}")

            # Check SearXNG health
            if not self.searxng.health_check():
                logger.error(f"SearXNG not responding at {config.SEARXNG_URL}")
                return False

            logger.info("SearXNG health check passed")

            # Main message loop
            if config.USE_STDIO:
                self._run_stdio_mode()
            else:
                logger.info("MCP Server ready for requests")
                import signal
                signal.pause()

        except Exception as e:
            logger.error(f"Error running server: {e}")
            return False

    def _run_stdio_mode(self):
        """Run in stdio mode for MCP protocol"""
        logger.info("Running in stdio mode")

        try:
            while True:
                try:
                    line = sys.stdin.readline()
                    if not line:
                        break

                    request = json.loads(line)
                    response = self.handle_request(request)

                    print(json.dumps(response))
                    sys.stdout.flush()

                except json.JSONDecodeError:
                    logger.error("Invalid JSON received")
                    print(json.dumps({"error": "Invalid JSON"}))
                    sys.stdout.flush()
                except Exception as e:
                    logger.error(f"Error processing request: {e}")
                    print(json.dumps({"error": str(e)}))
                    sys.stdout.flush()

        except KeyboardInterrupt:
            logger.info("Server interrupted")
        finally:
            self.monitor.cleanup()
            logger.info("Server stopped")


if __name__ == "__main__":
    server = CulinaryTrendMCPServer()
    server.run()
