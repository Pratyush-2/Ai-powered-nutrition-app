"""AI monitoring and metrics collection."""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, Any
from pathlib import Path


class AIMonitoring:
    """Monitors AI service performance and usage."""

    def __init__(self, db_path: str = "ai_metrics.db"):
        """Initialize the monitoring system."""
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                service_type TEXT,
                prediction TEXT,
                confidence REAL,
                input_data TEXT,
                output_data TEXT,
                processing_time REAL,
                metadata TEXT
            )
        """)

        # Create retrieval metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS retrieval_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                query TEXT,
                retrieved_count INTEGER,
                top_score REAL
            )
        """)

        conn.commit()
        conn.close()

    def log_prediction(
        self,
        user_id: int,
        service_type: str,
        prediction: str,
        confidence: float,
        input_data: Dict,
        output_data: Dict,
        processing_time: float,
        metadata: Dict = None
    ):
        """Log a prediction event."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ai_metrics (
                user_id,
                service_type,
                prediction,
                confidence,
                input_data,
                output_data,
                processing_time,
                metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            service_type,
            prediction,
            confidence,
            json.dumps(input_data),
            json.dumps(output_data),
            processing_time,
            json.dumps(metadata) if metadata else None
        ))

        conn.commit()
        conn.close()

    def log_retrieval_hit(
        self,
        query: str,
        retrieved_count: int,
        top_score: float,
        user_id: int = None
    ):
        """Log a retrieval event."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO retrieval_metrics (
                user_id,
                query,
                retrieved_count,
                top_score
            ) VALUES (?, ?, ?, ?)
        """, (
            user_id,
            query,
            retrieved_count,
            top_score
        ))

        conn.commit()
        conn.close()

    def get_prediction_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get prediction metrics for the specified time period."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        start_date = datetime.now() - timedelta(days=days)

        # Get total predictions
        cursor.execute("""
            SELECT COUNT(*) FROM ai_metrics
            WHERE timestamp >= ?
        """, (start_date.isoformat(),))
        total_predictions = cursor.fetchone()[0]

        # Get average confidence
        cursor.execute("""
            SELECT AVG(confidence) FROM ai_metrics
            WHERE timestamp >= ?
        """, (start_date.isoformat(),))
        avg_confidence = cursor.fetchone()[0]

        # Get average processing time
        cursor.execute("""
            SELECT AVG(processing_time) FROM ai_metrics
            WHERE timestamp >= ?
        """, (start_date.isoformat(),))
        avg_processing_time = cursor.fetchone()[0]

        # Get service type breakdown
        cursor.execute("""
            SELECT service_type, COUNT(*) FROM ai_metrics
            WHERE timestamp >= ?
            GROUP BY service_type
        """, (start_date.isoformat(),))
        service_breakdown = dict(cursor.fetchall())

        conn.close()

        return {
            "total_predictions": total_predictions,
            "average_confidence": round(avg_confidence, 3) if avg_confidence else 0,
            "average_processing_time": round(avg_processing_time, 3) if avg_processing_time else 0,
            "service_breakdown": service_breakdown
        }

    def get_retrieval_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get retrieval metrics for the specified time period."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        start_date = datetime.now() - timedelta(days=days)

        # Get total queries
        cursor.execute("""
            SELECT COUNT(*) FROM retrieval_metrics
            WHERE timestamp >= ?
        """, (start_date.isoformat(),))
        total_queries = cursor.fetchone()[0]

        # Get average retrieved count
        cursor.execute("""
            SELECT AVG(retrieved_count) FROM retrieval_metrics
            WHERE timestamp >= ?
        """, (start_date.isoformat(),))
        avg_retrieved = cursor.fetchone()[0]

        # Get average top score
        cursor.execute("""
            SELECT AVG(top_score) FROM retrieval_metrics
            WHERE timestamp >= ?
        """, (start_date.isoformat(),))
        avg_top_score = cursor.fetchone()[0]

        conn.close()

        return {
            "total_queries": total_queries,
            "average_retrieved": round(avg_retrieved, 2) if avg_retrieved else 0,
            "average_top_score": round(avg_top_score, 3) if avg_top_score else 0
        }