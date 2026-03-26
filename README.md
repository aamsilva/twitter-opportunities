# Twitter Opportunities

Find jobs, investments, and co-founders on Twitter. Automatically search for opportunities and store them in a local database.

## Features

- 🔍 **Job Search** - Find #hiring, job openings, remote jobs
- 💰 **Investment Opportunities** - Track #funding, seed rounds, angel investors  
- 🤝 **Co-founder Matching** - Find looking for co-founder tweets
- 📊 **Engagement Scoring** - Prioritize high-engagement opportunities
- 💾 **Local Storage** - SQLite database for offline access

## Installation

```bash
# Clone the repo
git clone https://github.com/aamsilva/twitter-opportunities.git
cd twitter-opportunities

# Install dependencies
pip install -r requirements.txt

# Set Twitter API token
export TWITTER_BEARER_TOKEN="your_bearer_token_here"
```

## Usage

### Collect Opportunities

Search Twitter and save new opportunities:
```bash
python main.py collect --hours 24 --max 10
```

### View Recent

Show recently collected opportunities:
```bash
python main.py recent                    # All types
python main.py recent --type job         # Jobs only
python main.py recent --type investment  # Investments only
python main.py recent --type cofounder   # Co-founders only
```

### View New

Show unread opportunities:
```bash
python main.py new           # All new
python main.py new --type job
```

### Export

Export to JSON:
```bash
python main.py export --output my_opportunities.json
```

## Configuration

Edit `src/config.py` to customize:

- Search queries for each category
- Database path
- Twitter API credentials

## Requirements

- Python 3.8+
- tweepy
- pandas

## License

MIT