# Social Media Sentiment Analysis: Auth0

This project performs sentiment analysis on social media posts about "Auth0" using Python. It currently supports Stack Overflow and Reddit data sources.

## Features

- **Stack Overflow Analysis**: Fetches questions and answers tagged with "auth0" and analyzes sentiment
- **Reddit Analysis**: Searches multiple subreddits for posts containing "auth0" and analyzes sentiment
- **Monthly Aggregation**: Groups data by month with total counts displayed on charts
- **CSV Export**: Saves all raw data to CSV files for further analysis
- **Intuitive Color Coding**: Red for negative, green for positive, blue for neutral sentiment

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/stephenrmoreno/sentiment-analysis.git
   cd sentiment-analysis
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Stack Overflow Analysis

1. Run the Stack Overflow script:
   ```bash
   python3 stackoverflow_sentiment.py
   ```

2. The script will:
   - Fetch recent Stack Overflow questions tagged with "auth0"
   - Perform sentiment analysis on titles and content
   - Display a monthly sentiment distribution chart
   - Save raw data to `stackoverflow_auth0_sentiment_data.csv`

### Reddit Analysis

1. Run the Reddit script:
   ```bash
   python3 reddit_sentiment.py
   ```

2. The script will:
   - Search multiple subreddits (programming, webdev, javascript, python, reactjs) for "auth0" posts
   - Fetch both posts and comments
   - Perform sentiment analysis on the content
   - Display a monthly sentiment distribution chart
   - Save raw data to `reddit_auth0_sentiment_data.csv`

## Configuration

### Stack Overflow Script
- **Tag**: Change `tag = 'auth0'` to analyze different technologies
- **Pages**: Adjust `pages = 5` to fetch more or fewer posts
- **Rate Limiting**: Built-in delays to respect Stack Overflow API limits

### Reddit Script
- **Subreddits**: Modify `subreddits` list to search different communities
- **Search Term**: Change `search_term = 'auth0'` to analyze different topics
- **Time Period**: Adjust `timeframe = 'year'` (options: hour, day, week, month, year, all)

## Output

Both scripts provide:
- **Interactive Charts**: Monthly sentiment distribution with total counts
- **Summary Statistics**: Sentiment breakdown and average scores
- **CSV Data**: Complete dataset for further analysis
- **Console Output**: Detailed statistics and data information

## Data Sources

- **Stack Overflow**: Uses the public Stack Overflow API (no authentication required)
- **Reddit**: Uses Reddit's JSON API (no authentication required)

## Rate Limiting

- **Stack Overflow**: Conservative rate limiting with automatic retry on 429 errors
- **Reddit**: Respectful delays between requests to avoid overwhelming servers

## Files

- `stackoverflow_sentiment.py` - Stack Overflow sentiment analysis
- `reddit_sentiment.py` - Reddit sentiment analysis
- `requirements.txt` - Python dependencies
- `.gitignore` - Excludes CSV files and cache

## Contributing

Feel free to submit issues and enhancement requests! 