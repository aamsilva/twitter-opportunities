"""Store and manage collected opportunities."""
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from .config import config


class OpportunityStore:
    """SQLite storage for opportunities."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.db_path
        self._init_db()
    
    def _init_db(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                query TEXT,
                text TEXT,
                username TEXT,
                name TEXT,
                created_at TEXT,
                collected_at TEXT,
                engagement_score INTEGER DEFAULT 0,
                is_new INTEGER DEFAULT 1
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_type ON opportunities(type)
        """)
        
        conn.commit()
        conn.close()
    
    def save(self, opportunities: Dict[str, List[Dict]]) -> int:
        """Save new opportunities to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved = 0
        collected_at = datetime.utcnow().isoformat()
        
        for op_type, tweets in opportunities.items():
            for tweet in tweets:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO opportunities 
                        (id, type, query, text, username, name, created_at, collected_at, engagement_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        tweet["id"],
                        op_type,
                        tweet.get("query"),
                        tweet["text"],
                        tweet["author"]["username"],
                        tweet["author"]["name"],
                        tweet.get("created_at"),
                        collected_at,
                        tweet.get("metrics", {}).get("like_count", 0) +
                        tweet.get("metrics", {}).get("retweet_count", 0)
                    ))
                    if cursor.rowcount:
                        saved += 1
                except Exception as e:
                    pass
        
        conn.commit()
        conn.close()
        return saved
    
    def get_recent(self, op_type: str = None, limit: int = 20) -> List[Dict]:
        """Get recent opportunities."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if op_type:
            cursor.execute("""
                SELECT * FROM opportunities 
                WHERE type = ?
                ORDER BY engagement_score DESC, collected_at DESC
                LIMIT ?
            """, (op_type, limit))
        else:
            cursor.execute("""
                SELECT * FROM opportunities 
                ORDER BY engagement_score DESC, collected_at DESC
                LIMIT ?
            """, (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_new(self, op_type: str = None) -> List[Dict]:
        """Get new (unread) opportunities."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if op_type:
            cursor.execute("""
                SELECT * FROM opportunities 
                WHERE is_new = 1 AND type = ?
                ORDER BY collected_at DESC
            """, (op_type,))
        else:
            cursor.execute("""
                SELECT * FROM opportunities 
                WHERE is_new = 1
                ORDER BY collected_at DESC
            """)
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def mark_read(self, opportunity_id: str):
        """Mark opportunity as read."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE opportunities SET is_new = 0 WHERE id = ?", (opportunity_id,))
        conn.commit()
        conn.close()
    
    def mark_all_read(self, op_type: str = None):
        """Mark all opportunities as read."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if op_type:
            cursor.execute("UPDATE opportunities SET is_new = 0 WHERE type = ?", (op_type,))
        else:
            cursor.execute("UPDATE opportunities SET is_new = 0")
        conn.commit()
        conn.close()
    
    def export_json(self, filepath: str = "opportunities.json"):
        """Export all opportunities to JSON."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM opportunities ORDER BY collected_at DESC")
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            data.append({
                "id": row[0],
                "type": row[1],
                "query": row[2],
                "text": row[3],
                "username": row[4],
                "name": row[5],
                "created_at": row[6],
                "collected_at": row[7],
                "engagement_score": row[8],
                "is_new": row[9],
            })
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        conn.close()
        return filepath


if __name__ == "__main__":
    store = OpportunityStore()
    print(f"Database: {store.db_path}")
    print(f"Recent opportunities: {len(store.get_recent())}")