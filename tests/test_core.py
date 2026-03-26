"""Tests for Twitter Opportunities."""
import os
import sys
import tempfile

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import OpportunityConfig
from src.storage import OpportunityStore


def test_config():
    """Test configuration."""
    config = OpportunityConfig()
    assert len(config.job_queries) > 0
    assert len(config.investment_queries) > 0
    assert len(config.cofounder_queries) > 0
    print("✓ Config test passed")


def test_storage():
    """Test storage functionality."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    try:
        store = OpportunityStore(db_path)
        
        # Test save
        test_data = {
            "jobs": [{
                "id": "test123",
                "text": "Test job opportunity",
                "author": {"username": "testuser", "name": "Test User"},
                "query": "#hiring",
                "created_at": "2024-01-01T00:00:00",
                "metrics": {"like_count": 5, "retweet_count": 2}
            }],
            "investments": [],
            "cofounder": []
        }
        
        saved = store.save(test_data)
        assert saved == 1, f"Expected 1 saved, got {saved}"
        
        # Test get_recent (use plural form to match DB)
        recent = store.get_recent("jobs", 10)
        assert len(recent) == 1
        assert recent[0]["username"] == "testuser"
        
        # Test get_new (use plural form)
        new = store.get_new("jobs")
        assert len(new) == 1
        
        # Test mark_read
        store.mark_read("test123")
        new_after = store.get_new("jobs")
        assert len(new_after) == 0
        
        print("✓ Storage test passed")
        
    finally:
        os.unlink(db_path)


def test_storage_multiple():
    """Test storage with multiple entries."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    try:
        store = OpportunityStore(db_path)
        
        test_data = {
            "jobs": [
                {"id": f"job{i}", "text": f"Job {i}", "author": {"username": f"user{i}", "name": f"User {i}"}, "query": "test", "created_at": "2024-01-01", "metrics": {}}
                for i in range(5)
            ],
            "investments": [],
            "cofounder": []
        }
        
        saved = store.save(test_data)
        assert saved == 5
        
        recent = store.get_recent("jobs")
        assert len(recent) == 5
        
        print("✓ Multiple storage test passed")
        
    finally:
        os.unlink(db_path)


if __name__ == "__main__":
    test_config()
    test_storage()
    test_storage_multiple()
    print("\n✅ All tests passed!")