"""
Monitoring and analytics for the AI pipeline.

This module handles logging of model predictions, user feedback,
and retrieval hits for analytics and model improvement.
"""

import csv
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)

class AIMonitoring:
    """Handles monitoring and analytics for AI services."""
    
    def __init__(self, db_path: str = "ai_metrics.db"):
        self.db_path = Path(db_path)
        self.csv_path = self.db_path.with_suffix(".csv")
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for metrics storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                service_type TEXT,
                prediction TEXT,
                confidence REAL,
                input_data TEXT,
                output_data TEXT,
                processing_time REAL,
                feedback_score INTEGER,
                feedback_text TEXT,
                metadata TEXT
            )
        """)
        
        # Create retrieval hits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS retrieval_hits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                query TEXT,
                retrieved_count INTEGER,
                top_score REAL,
                user_id INTEGER,
                service_type TEXT
            )
        """)
        
        # Create user feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                prediction_id INTEGER,
                feedback_type TEXT,
                feedback_score INTEGER,
                feedback_text TEXT,
                corrected_prediction TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_prediction(self, user_id: int, service_type: str, prediction: str, 
                      confidence: float, input_data: Dict, output_data: Dict,
                      processing_time: float, metadata: Dict = None):
        """
        Log a model prediction.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ai_metrics 
                (user_id, service_type, prediction, confidence, input_data, 
                 output_data, processing_time, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                service_type,
                prediction,
                confidence,
                json.dumps(input_data),
                json.dumps(output_data),
                processing_time,
                json.dumps(metadata or {})
            ))
            
            conn.commit()
            conn.close()
            
            # Also log to CSV for easy analysis
            self._log_to_csv({
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'service_type': service_type,
                'prediction': prediction,
                'confidence': confidence,
                'processing_time': processing_time
            })
            
        except Exception as e:
            logger.error(f"Error logging prediction: {e}")
    
    def log_retrieval_hit(self, query: str, retrieved_count: int, top_score: float,
                         user_id: int = None, service_type: str = "retrieval"):
        """
        Log a retrieval operation.
        
        Args:
            query: Search query used
            retrieved_count: Number of results retrieved
            top_score: Score of the top result
            user_id: ID of the user (optional)
            service_type: Type of service
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO retrieval_hits 
                (query, retrieved_count, top_score, user_id, service_type)
                VALUES (?, ?, ?, ?, ?)
            """, (query, retrieved_count, top_score, user_id, service_type))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging retrieval hit: {e}")
    
    def log_user_feedback(self, user_id: int, prediction_id: int, feedback_type: str,
                         feedback_score: int, feedback_text: str = None,
                         corrected_prediction: str = None):
        """
        Log user feedback on predictions.
        
        Args:
            user_id: ID of the user
            prediction_id: ID of the prediction being feedback on
            feedback_type: Type of feedback (positive, negative, correction)
            feedback_score: Score given by user (1-5)
            feedback_text: Text feedback from user
            corrected_prediction: Corrected prediction if applicable
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_feedback 
                (user_id, prediction_id, feedback_type, feedback_score, 
                 feedback_text, corrected_prediction)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, prediction_id, feedback_type, feedback_score,
                  feedback_text, corrected_prediction))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging user feedback: {e}")
    
    def _log_to_csv(self, data: Dict):
        """Log data to CSV file for easy analysis."""
        try:
            file_exists = self.csv_path.exists()
            
            with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(data)
                
        except Exception as e:
            logger.error(f"Error logging to CSV: {e}")
    
    def get_prediction_metrics(self, days: int = 7) -> Dict:
        """
        Get prediction metrics for the last N days.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total predictions
            cursor.execute("""
                SELECT COUNT(*) FROM ai_metrics 
                WHERE timestamp >= datetime('now', '-{} days')
            """.format(days))
            total_predictions = cursor.fetchone()[0]
            
            # Get predictions by service type
            cursor.execute("""
                SELECT service_type, COUNT(*) as count, AVG(confidence) as avg_confidence
                FROM ai_metrics 
                WHERE timestamp >= datetime('now', '-{} days')
                GROUP BY service_type
            """.format(days))
            
            # Get service metrics
            cursor.execute("""
                SELECT service_type, COUNT(*) FROM ai_metrics 
                WHERE timestamp >= datetime('now', '-{} days')
                GROUP BY service_type
            """.format(days))
            
            fetched_rows_service_metrics = cursor.fetchall()
            service_metrics = {}
            for row in fetched_rows_service_metrics:
                if len(row) >= 2:
                    service_metrics[row[0]] = row[1]
                else:
                    # logger.warning(f"Skipping row in service_metrics due to insufficient elements: {row}")
            
            # Get average processing time
            cursor.execute("""
                SELECT AVG(processing_time) FROM ai_metrics 
                WHERE timestamp >= datetime('now', '-{} days')
            """.format(days))
            avg_processing_time = cursor.fetchone()[0] or 0
            
            # Get confidence distribution
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN confidence >= 0.8 THEN 'high'
                        WHEN confidence >= 0.6 THEN 'medium'
                        ELSE 'low'
                    END as confidence_level,
                    COUNT(*) as count
                FROM ai_metrics 
                WHERE timestamp >= datetime('now', '-{} days')
                GROUP BY confidence_level
            """.format(days))
            
            fetched_rows = cursor.fetchall()
            
            confidence_distribution = {}
            for row in fetched_rows:
                if len(row) >= 2:
                    confidence_distribution[row[0]] = row[1]
                else:
                    # logger.warning(f"Skipping row in confidence_distribution due to insufficient elements: {row}")
            
            conn.close()
            
            return {
                'total_predictions': total_predictions,
                'service_metrics': service_metrics,
                'avg_processing_time': avg_processing_time,
                'confidence_distribution': confidence_distribution,
                'days': days
            }
            
        except Exception as e:
            logger.error(f"Error getting prediction metrics: {e}")
            return {}
    
    def get_retrieval_metrics(self, days: int = 7) -> Dict:
        """
        Get retrieval metrics for the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary with retrieval metrics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total retrievals
            cursor.execute("""
                SELECT COUNT(*) FROM retrieval_hits 
                WHERE timestamp >= datetime('now', '-{} days')
            """.format(days))
            total_retrievals = cursor.fetchone()[0]
            
            # Get average scores
            cursor.execute("""
                SELECT AVG(top_score), AVG(retrieved_count) FROM retrieval_hits 
                WHERE timestamp >= datetime('now', '-{} days')
            """.format(days))
            avg_score, avg_count = cursor.fetchone()
            
            # Get top queries
            cursor.execute("""
                SELECT query, COUNT(*) as frequency FROM retrieval_hits 
                WHERE timestamp >= datetime('now', '-{} days')
                GROUP BY query
                ORDER BY frequency DESC
                LIMIT 10
            """.format(days))
            top_queries = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_retrievals': total_retrievals,
                'avg_score': avg_score or 0,
                'avg_retrieved_count': avg_count or 0,
                'top_queries': top_queries,
                'days': days
            }
            
        except Exception as e:
            logger.error(f"Error getting retrieval metrics: {e}")
            return {}
    
    def get_user_feedback_metrics(self, days: int = 7) -> Dict:
        """
        Get user feedback metrics for the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary with feedback metrics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total feedback
            cursor.execute("""
                SELECT COUNT(*) FROM user_feedback 
                WHERE timestamp >= datetime('now', '-{} days')
            """.format(days))
            total_feedback = cursor.fetchone()[0]
            
            # Get feedback by type
            cursor.execute("""
                SELECT feedback_type, COUNT(*) as count, AVG(feedback_score) as avg_score
                FROM user_feedback 
                WHERE timestamp >= datetime('now', '-{} days')
                GROUP BY feedback_type
            """.format(days))
            feedback_by_type = dict(cursor.fetchall())
            
            # Get average feedback score
            cursor.execute("""
                SELECT AVG(feedback_score) FROM user_feedback 
                WHERE timestamp >= datetime('now', '-{} days')
            """.format(days))
            avg_feedback_score = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_feedback': total_feedback,
                'feedback_by_type': feedback_by_type,
                'avg_feedback_score': avg_feedback_score,
                'days': days
            }
            
        except Exception as e:
            logger.error(f"Error getting feedback metrics: {e}")
            return {}
    
    def export_metrics_to_csv(self, output_path: str = None):
        """
        Export all metrics to CSV files.
        
        Args:
            output_path: Output directory for CSV files
        """
        if output_path is None:
            output_path = self.db_path.parent / "exports"
        
        output_path = Path(output_path)
        output_path.mkdir(exist_ok=True)
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Export each table
            tables = ['ai_metrics', 'retrieval_hits', 'user_feedback']
            
            for table in tables:
                df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                df.to_csv(output_path / f"{table}.csv", index=False)
            
            conn.close()
            logger.info(f"Metrics exported to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")


# Global monitoring instance
_monitoring_instance = None

def get_monitoring() -> AIMonitoring:
    """Get the global monitoring instance."""
    global _monitoring_instance
    if _monitoring_instance is None:
        _monitoring_instance = AIMonitoring()
    return _monitoring_instance

def log_prediction(user_id: int, service_type: str, prediction: str, 
                  confidence: float, input_data: Dict, output_data: Dict,
                  processing_time: float, metadata: Dict = None):
    """Convenience function to log prediction."""
    monitoring = get_monitoring()
    monitoring.log_prediction(user_id, service_type, prediction, confidence,
                            input_data, output_data, processing_time, metadata)

def log_retrieval_hit(query: str, retrieved_count: int, top_score: float,
                     user_id: int = None, service_type: str = "retrieval"):
    """Convenience function to log retrieval hit."""
    monitoring = get_monitoring()
    monitoring.log_retrieval_hit(query, retrieved_count, top_score, user_id, service_type)

