"""Configuration for Twitter Opportunities."""
import os
from dataclasses import dataclass
from typing import List


@dataclass
class OpportunityConfig:
    """Configuration for opportunity search."""
    
    # Search queries for different opportunity types
    job_queries: List[str] = None
    investment_queries: List[str] = None
    cofounder_queries: List[str] = None
    
    # Twitter API credentials
    bearer_token: str = None
    
    # Storage
    db_path: str = "opportunities.db"
    
    def __post_init__(self):
        if self.job_queries is None:
            self.job_queries = [
                "#hiring",
                "#jobopening", 
                "hiring engineer",
                "looking for developer",
                "#remotejobs",
                "job opportunity",
            ]
        if self.investment_queries is None:
            self.investment_queries = [
                "#funding",
                "#startup",
                "looking for investor",
                "seed round",
                "Series A",
                "angel investing",
            ]
        if self.cofounder_queries is None:
            self.cofounder_queries = [
                "looking for co-founder",
                "co-founder wanted",
                "founder partnership",
                "startup partner",
            ]
        if self.bearer_token is None:
            self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")


# Default config
config = OpportunityConfig()