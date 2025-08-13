import requests
import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
import datetime
from datetime import datetime as dt
import time
import json

# --- Reddit API configuration ---
# Using Reddit's JSON API (no authentication required for public data)
BASE_URL = "https://www.reddit.com"

def fetch_reddit_data(subreddits, search_term, limit=100, timeframe='year'):
    """
    Fetch posts and comments from multiple subreddits
    """
    all_data = []
    
    headers = {
        'User-Agent': 'SentimentAnalysisBot/1.0 (by /u/your_username)'
    }
    
    for subreddit in subreddits:
        try:
            print(f"Fetching posts from r/{subreddit}...")
            
            # Method 1: Search within subreddit
            url = f"{BASE_URL}/r/{subreddit}/search.json"
            params = {
                'q': search_term,
                'restrict_sr': 'on',
                't': timeframe,
                'limit': limit,
                'sort': 'new'
            }
            
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and 'children' in data['data']:
                for post in data['data']['children']:
                    post_data = post['data']
                    
                    # Only include posts that actually contain the search term
                    title = post_data.get('title', '').lower()
                    body = post_data.get('selftext', '').lower()
                    if search_term.lower() in title or search_term.lower() in body:
                        all_data.append({
                            'type': 'post',
                            'title': post_data.get('title', ''),
                            'body': post_data.get('selftext', ''),
                            'score': post_data.get('score', 0),
                            'created_date': dt.fromtimestamp(post_data.get('created_utc', 0)).date(),
                            'subreddit': subreddit,
                            'url': post_data.get('url', ''),
                            'num_comments': post_data.get('num_comments', 0)
                        })
                        
                        # Fetch comments for this post
                        post_id = post_data.get('id')
                        if post_id and post_data.get('num_comments', 0) > 0:
                            comments = fetch_post_comments(post_id, subreddit, headers)
                            all_data.extend(comments)
            
            # Method 2: Get recent posts and filter
            url = f"{BASE_URL}/r/{subreddit}/new.json"
            params = {
                'limit': limit
            }
            
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and 'children' in data['data']:
                for post in data['data']['children']:
                    post_data = post['data']
                    
                    # Check if post contains search term
                    title = post_data.get('title', '').lower()
                    body = post_data.get('selftext', '').lower()
                    if search_term.lower() in title or search_term.lower() in body:
                        all_data.append({
                            'type': 'post',
                            'title': post_data.get('title', ''),
                            'body': post_data.get('selftext', ''),
                            'score': post_data.get('score', 0),
                            'created_date': dt.fromtimestamp(post_data.get('created_utc', 0)).date(),
                            'subreddit': subreddit,
                            'url': post_data.get('url', ''),
                            'num_comments': post_data.get('num_comments', 0)
                        })
                        
                        # Fetch comments for this post
                        post_id = post_data.get('id')
                        if post_id and post_data.get('num_comments', 0) > 0:
                            comments = fetch_post_comments(post_id, subreddit, headers)
                            all_data.extend(comments)
            
            time.sleep(1)  # Be respectful to Reddit's servers
            
        except requests.RequestException as e:
            print(f"Error fetching posts from r/{subreddit}: {e}")
            continue
    
    return all_data

def fetch_post_comments(post_id, subreddit, headers, limit=50):
    """
    Fetch comments for a specific post
    """
    comments = []
    
    try:
        url = f"{BASE_URL}/r/{subreddit}/comments/{post_id}.json"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if len(data) > 1 and 'data' in data[1] and 'children' in data[1]['data']:
            for comment in data[1]['data']['children']:
                if comment['kind'] == 't1':  # Regular comment
                    comment_data = comment['data']
                    
                    # Skip deleted/removed comments
                    if comment_data.get('body') not in ['[deleted]', '[removed]']:
                        comments.append({
                            'type': 'comment',
                            'title': '',  # Comments don't have titles
                            'body': comment_data.get('body', ''),
                            'score': comment_data.get('score', 0),
                            'created_date': dt.fromtimestamp(comment_data.get('created_utc', 0)).date(),
                            'subreddit': subreddit,
                            'url': '',
                            'num_comments': 0
                        })
        
        time.sleep(0.5)  # Rate limiting
        
    except requests.RequestException as e:
        print(f"Error fetching comments for post {post_id}: {e}")
    
    return comments

def clean_text(text):
    """
    Clean Reddit text (remove markdown, special characters, etc.)
    """
    import re
    if not text:
        return ""
    
    # Remove markdown links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Remove markdown formatting
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
    text = re.sub(r'`([^`]+)`', r'\1', text)        # Code
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-\:]', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def get_sentiment(text):
    """
    Analyze sentiment of text using TextBlob
    """
    if not text or len(text.strip()) < 3:
        return 'neutral'
    
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return 'positive'
    elif polarity < -0.1:
        return 'negative'
    else:
        return 'neutral'

def main():
    # --- Configuration ---
    subreddits = ['programming', 'webdev', 'javascript', 'python', 'reactjs','auth0','authentication','oauth']  # Multiple subreddits
    search_term = 'auth0'  # Change this to any search term
    limit = 100  # Number of posts to fetch per subreddit
    timeframe = 'year'  # Time period: hour, day, week, month, year, all
    
    print(f"Fetching Reddit data from multiple subreddits for term: {search_term}")
    print(f"Subreddits: {', '.join(subreddits)}")
    print("This may take a few minutes...")
    
    # Fetch data from Reddit
    data = fetch_reddit_data(subreddits, search_term, limit=limit, timeframe=timeframe)
    
    if not data:
        print('No data found for the specified search term.')
        print('Trying with broader search terms...')
        
        # Try broader terms
        broader_terms = ['authentication', 'oauth', 'login', 'security']
        for term in broader_terms:
            print(f"Trying search term: {term}")
            data = fetch_reddit_data(subreddits, term, limit=limit, timeframe=timeframe)
            if data:
                search_term = term
                break
        
        if not data:
            print('No data found even with broader terms.')
            return
    
    print(f"Fetched {len(data)} items from Reddit")
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Clean text data
    df['clean_body'] = df['body'].apply(clean_text)
    df['clean_title'] = df['title'].apply(clean_text)
    
    # Combine title and body for sentiment analysis
    df['combined_text'] = df['clean_title'] + ' ' + df['clean_body']
    
    # Perform sentiment analysis
    df['sentiment'] = df['combined_text'].apply(get_sentiment)
    
    # Add month column for aggregation
    df['month'] = df['created_date'].apply(lambda d: d.replace(day=1))
    
    # Group by month and sentiment, count items
    counts = df.groupby(['month', 'sentiment']).size().unstack(fill_value=0)
    
    # Calculate total counts per month for annotations
    total_counts = counts.sum(axis=1)
    
    # Normalize to 100% stacked (percentage per month)
    percentages = counts.div(counts.sum(axis=1), axis=0) * 100
    
    # Plot 100% stacked bar chart
    plt.figure(figsize=(12, 8))
    # Ensure correct color mapping: negative=red, neutral=blue, positive=green
    color_map = {'negative': 'red', 'neutral': 'blue', 'positive': 'green'}
    colors = [color_map.get(col, 'gray') for col in percentages.columns]
    ax = percentages.plot(kind='bar', stacked=True, color=colors)
    plt.title(f'Sentiment Analysis of Reddit {search_term} Posts by Month (100% Stacked)')
    plt.xlabel('Month')
    plt.ylabel('Percentage of Posts (%)')
    plt.legend(title='Sentiment')
    plt.xticks(rotation=45)
    
    # Add total count annotations on top of each bar
    for i, (month, total) in enumerate(total_counts.items()):
        plt.text(i, 102, f'n={total}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.show()
    
    # Print summary statistics
    print("\n=== Summary Statistics ===")
    print(f"Total posts analyzed: {len(df)}")
    print(f"Date range: {df['created_date'].min()} to {df['created_date'].max()}")
    print("\nSentiment distribution:")
    sentiment_counts = df['sentiment'].value_counts()
    for sentiment, count in sentiment_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {sentiment.capitalize()}: {count} ({percentage:.1f}%)")
    
    print(f"\nAverage score by sentiment:")
    score_by_sentiment = df.groupby('sentiment')['score'].mean()
    for sentiment, avg_score in score_by_sentiment.items():
        print(f"  {sentiment.capitalize()}: {avg_score:.2f}")
    
    print(f"\nPosts vs Comments breakdown:")
    type_counts = df['type'].value_counts()
    for post_type, count in type_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {post_type.capitalize()}: {count} ({percentage:.1f}%)")
    
    # Save raw data to CSV
    csv_filename = f"reddit_{search_term}_sentiment_data.csv"
    df.to_csv(csv_filename, index=False)
    print(f"\n=== Raw Data Saved ===")
    print(f"Complete dataset saved to: {csv_filename}")
    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")

if __name__ == "__main__":
    main()
