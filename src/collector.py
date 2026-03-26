"""Twitter API collector for opportunities."""
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

try:
    import tweepy
except ImportError:
    tweepy = None

from .config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterCollector:
    """Collect tweets matching opportunity keywords."""
    
    def __init__(self, bearer_token: str = None):
        if tweepy is None:
            raise ImportError("tweepy is required. Install: pip install tweepy")
        
        self.bearer_token = bearer_token or config.bearer_token
        if not self.bearer_token:
            raise ValueError("Twitter bearer token required")
        
        self.client = tweepy.Client(bearer_token=self.bearer_token)
    
    def search_recent(
        self, 
        query: str, 
        max_results: int = 10,
        start_time: datetime = None
    ) -> List[Dict]:
        """Search recent tweets matching query."""
        try:
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                start_time=start_time.isoformat() if start_time else None,
                tweet_fields=["created_at", "author_id", "text", "public_metrics"],
                expansions=["author_id"],
                user_fields=["username", "name", "public_metrics"]
            )
            
            if not tweets.data:
                return []
            
            results = []
            users = {u.id: u for u in (tweets.includes.get("users") or [])}
            
            for tweet in tweets.data:
                user = users.get(tweet.author_id)
                results.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                    "author": {
                        "id": tweet.author_id,
                        "username": user.username if user else None,
                        "name": user.name if user else None,
                    },
                    "metrics": tweet.public_metrics or {},
                })
            
            logger.info(f"Found {len(results)} tweets for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching {query}: {e}")
            return []
    
    def collect_opportunities(
        self, 
        hours_back: int = 24,
        max_per_query: int = 10
    ) -> Dict[str, List[Dict]]:
        """Collect all opportunity types."""
        from datetime import timedelta
        
        start_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        all_opportunities = {
            "jobs": [],
            "investments": [],
            "cofounder": [],
        }
        
        # Collect jobs
        for query in config.job_queries:
            tweets = self.search_recent(
                f"{query} -is:retweet",
                max_results=max_per_query,
                start_time=start_time
            )
            for tweet in tweets:
                tweet["type"] = "job"
                tweet["query"] = query
            all_opportunities["jobs"].extend(tweets)
        
        # Collect investments
        for query in config.investment_queries:
            tweets = self.search_recent(
                f"{query} -is:retweet",
                max_results=max_per_query,
                start_time=start_time
            )
            for tweet in tweets:
                tweet["type"] = "investment"
                tweet["query"] = query
            all_opportunities["investments"].extend(tweets)
        
        # Collect co-founder
        for query in config.cofounder_queries:
            tweets = self.search_recent(
                f"{query} -is:retweet",
                max_results=max_per_query,
                start_time=start_time
            )
            for tweet in tweets:
                tweet["type"] = "cofounder"
                tweet["query"] = query
            all_opportunities["cofounder"].extend(tweets)
        
        return all_opportunities


if __name__ == "__main__":
    collector = TwitterCollector()
    results = collector.collect_opportunities(hours_back=24, max_per_query=5)
    
    print(f"\n📊 Opportunities found in last 24h:")
    print(f"  💼 Jobs: {len(results['jobs'])}")
    print(f"  💰 Investments: {len(results['investments'])}")
    print(f"  🤝 Co-founders: {len(results['cofounder'])}")
    
    for op_type, tweets in results.items():
        if tweets:
            print(f"\n--- {op_type.upper()} ---")
            for t in tweets[:3]:
                print(f"  @{t['author']['username']}: {t['text'][:100]}...")