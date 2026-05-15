"""
Database module for storing trend data and monitoring history
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import config

logger = logging.getLogger(__name__)


class TrendDatabase:
    """SQLite database for trend monitoring"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        self.conn = None
        self.init_db()

    def init_db(self):
        """Initialize database tables"""
        try:
            self.conn = sqlite3.connect(self.db_path, timeout=config.DATABASE_TIMEOUT)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()

            # Monitors table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS monitors (
                    monitoring_id TEXT PRIMARY KEY,
                    trend_name TEXT NOT NULL,
                    query TEXT NOT NULL,
                    platforms TEXT,
                    notes TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT,
                    updated_at TEXT
                )
            """
            )

            # Search results table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS search_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    monitoring_id TEXT NOT NULL,
                    title TEXT,
                    url TEXT NOT NULL UNIQUE,
                    snippet TEXT,
                    source TEXT,
                    platform TEXT,
                    image_url TEXT,
                    search_date TEXT,
                    FOREIGN KEY (monitoring_id) REFERENCES monitors(monitoring_id)
                )
            """
            )

            # Alerts table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    monitoring_id TEXT NOT NULL,
                    alert_type TEXT,
                    message TEXT,
                    new_results_count INTEGER DEFAULT 0,
                    created_at TEXT,
                    FOREIGN KEY (monitoring_id) REFERENCES monitors(monitoring_id)
                )
            """
            )

            # Trend analysis table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS trend_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    monitoring_id TEXT NOT NULL,
                    analysis_type TEXT,
                    pattern_data TEXT,
                    analysis_date TEXT,
                    FOREIGN KEY (monitoring_id) REFERENCES monitors(monitoring_id)
                )
            """
            )

            # Create indexes for performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_monitoring_id ON search_results(monitoring_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_search_date ON search_results(search_date)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_alert_date ON alerts(created_at)"
            )

            self.conn.commit()
            logger.info(f"Database initialized at {self.db_path}")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def add_monitor(
        self,
        monitoring_id: str,
        trend_name: str,
        query: str,
        platforms: str,
        notes: str = "",
    ) -> bool:
        """Add a new monitor"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO monitors
                (monitoring_id, trend_name, query, platforms, notes, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'active', ?, ?)
            """,
                (
                    monitoring_id,
                    trend_name,
                    query,
                    platforms,
                    notes,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to add monitor: {e}")
            return False

    def update_monitor_status(self, monitoring_id: str, status: str) -> bool:
        """Update monitor status"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                UPDATE monitors
                SET status = ?, updated_at = ?
                WHERE monitoring_id = ?
            """,
                (status, datetime.now().isoformat(), monitoring_id),
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update monitor status: {e}")
            return False

    def store_monitoring_results(
        self, monitoring_id: str, results: List[Dict[str, Any]]
    ) -> bool:
        """Store search results from monitoring"""
        try:
            cursor = self.conn.cursor()
            search_date = datetime.now().isoformat()

            for result in results:
                try:
                    cursor.execute(
                        """
                        INSERT INTO search_results
                        (monitoring_id, title, url, snippet, source, platform, image_url, search_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            monitoring_id,
                            result.get("title"),
                            result.get("url"),
                            result.get("snippet"),
                            result.get("source"),
                            result.get("platform"),
                            result.get("image_url"),
                            search_date,
                        ),
                    )
                except sqlite3.IntegrityError:
                    # URL already exists, skip
                    pass

            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to store monitoring results: {e}")
            return False

    def get_previous_results(self, monitoring_id: str) -> List[Dict[str, Any]]:
        """Get previous search results for change detection"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT * FROM search_results
                WHERE monitoring_id = ?
                ORDER BY search_date DESC
                LIMIT 50
            """,
                (monitoring_id,),
            )

            results = []
            for row in cursor.fetchall():
                results.append(dict(row))

            return results
        except Exception as e:
            logger.error(f"Failed to get previous results: {e}")
            return []

    def create_alert(
        self,
        monitoring_id: str,
        alert_type: str,
        message: str,
        new_results_count: int = 0,
    ) -> bool:
        """Create an alert"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO alerts
                (monitoring_id, alert_type, message, new_results_count, created_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    monitoring_id,
                    alert_type,
                    message,
                    new_results_count,
                    datetime.now().isoformat(),
                ),
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            return False

    def get_recent_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                SELECT a.*, m.trend_name FROM alerts a
                LEFT JOIN monitors m ON a.monitoring_id = m.monitoring_id
                ORDER BY a.created_at DESC
                LIMIT ?
            """,
                (limit,),
            )

            alerts = []
            for row in cursor.fetchall():
                alerts.append(dict(row))

            return alerts
        except Exception as e:
            logger.error(f"Failed to get recent alerts: {e}")
            return []

    def get_trend_history(
        self, trend_name: str, cutoff_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get trend history"""
        try:
            cursor = self.conn.cursor()
            cutoff_iso = cutoff_date.isoformat()

            cursor.execute(
                """
                SELECT sr.*, m.trend_name FROM search_results sr
                LEFT JOIN monitors m ON sr.monitoring_id = m.monitoring_id
                WHERE m.trend_name = ? AND sr.search_date > ?
                ORDER BY sr.search_date DESC
            """,
                (trend_name, cutoff_iso),
            )

            history = []
            for row in cursor.fetchall():
                history.append(dict(row))

            return history
        except Exception as e:
            logger.error(f"Failed to get trend history: {e}")
            return []

    def cleanup_old_data(self, retention_days: int = None):
        """Clean up old monitoring data"""
        try:
            retention = retention_days or config.MONITORING_RETENTION_DAYS
            cutoff_date = (datetime.now() - timedelta(days=retention)).isoformat()

            cursor = self.conn.cursor()

            # Delete old search results
            cursor.execute(
                "DELETE FROM search_results WHERE search_date < ?", (cutoff_date,)
            )

            # Delete old alerts
            cursor.execute(
                "DELETE FROM alerts WHERE created_at < ?", (cutoff_date,)
            )

            self.conn.commit()
            logger.info(f"Cleaned up data older than {retention} days")

        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
