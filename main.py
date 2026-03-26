#!/usr/bin/env python3
"""Twitter Opportunities - Find jobs, investments, and co-founders on Twitter."""
import argparse
import sys
from datetime import datetime

from src.config import config
from src.collector import TwitterCollector
from src.storage import OpportunityStore


def collect_and_store(hours_back: int = 24, max_per_query: int = 10):
    """Collect opportunities and store them."""
    print(f"🔍 Searching Twitter for opportunities (last {hours_back}h)...")
    
    collector = TwitterCollector()
    opportunities = collector.collect_opportunities(hours_back, max_per_query)
    
    store = OpportunityStore()
    saved = store.save(opportunities)
    
    print(f"\n✅ Collected & saved {saved} new opportunities:")
    print(f"   💼 Jobs: {len(opportunities['jobs'])}")
    print(f"   💰 Investments: {len(opportunities['investments'])}")
    print(f"   🤝 Co-founders: {len(opportunities['cofounder'])}")
    
    return opportunities


def show_recent(op_type: str = None, limit: int = 10):
    """Show recent opportunities."""
    store = OpportunityStore()
    opportunities = store.get_recent(op_type, limit)
    
    if not opportunities:
        print("No opportunities found. Run collect first!")
        return
    
    print(f"\n📋 Recent opportunities:")
    for i, op in enumerate(opportunities, 1):
        emoji = {"job": "💼", "investment": "💰", "cofounder": "🤝"}.get(op["type"], "📌")
        print(f"\n{i}. {emoji} @{op['username']} ({op['name']})")
        print(f"   {op['text'][:150]}...")
        print(f"   📊 Score: {op['engagement_score']} | {op['collected_at'][:10]}")


def show_new(op_type: str = None):
    """Show new (unread) opportunities."""
    store = OpportunityStore()
    opportunities = store.get_new(op_type)
    
    if not opportunities:
        print("✅ No new opportunities!")
        return
    
    print(f"\n🆕 {len(opportunities)} new opportunities:")
    for op in opportunities:
        emoji = {"job": "💼", "investment": "💰", "cofounder": "🤝"}.get(op["type"], "📌")
        print(f"\n{emoji} @{op['username']}: {op['text'][:120]}...")
    
    store.mark_all_read(op_type)
    print("\n✅ Marked all as read.")


def export_data(filepath: str = "opportunities.json"):
    """Export to JSON."""
    store = OpportunityStore()
    path = store.export_json(filepath)
    print(f"📦 Exported to {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Twitter Opportunities - Find jobs, investments, co-founders"
    )
    parser.add_argument(
        "command",
        choices=["collect", "recent", "new", "export"],
        help="Command to run"
    )
    parser.add_argument("--type", "-t", choices=["job", "investment", "cofounder"],
                        help="Filter by type")
    parser.add_argument("--hours", default=24, type=int,
                        help="Hours to look back (default: 24)")
    parser.add_argument("--max", default=10, type=int,
                        help="Max tweets per query (default: 10)")
    parser.add_argument("--limit", default=10, type=int,
                        help="Limit results (default: 10)")
    parser.add_argument("--output", "-o", default="opportunities.json",
                        help="Output file for export")
    
    args = parser.parse_args()
    
    if args.command == "collect":
        collect_and_store(args.hours, args.max)
    elif args.command == "recent":
        show_recent(args.type, args.limit)
    elif args.command == "new":
        show_new(args.type)
    elif args.command == "export":
        export_data(args.output)


if __name__ == "__main__":
    main()