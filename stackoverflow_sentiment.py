import requests
import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
import datetime
from datetime import datetime as dt
import time

# --- Stack Overflow API configuration ---
BASE_URL = "https://api.stackexchange.com/2.3"
SITE = "stackoverflow"

def fetch_stackoverflow_data(tag, pages=5, page_size=100):
    """
    Fetch questions from Stack Overflow API (more efficient - questions only)
    """
    all_data = []
    
    # Fetch questions only (more efficient, fewer API calls)
    for page in range(1, pages + 1):
        url = f"{BASE_URL}/questions"
        params = {
            'page': page,
            'pagesize': page_size,
            'order': 'desc',
            'sort': 'creation',
            'tagged': tag,
            'site': SITE,
            'filter': '!9Z(-wzu0T'  # Basic filter
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'items' in data:
                for item in data['items']:
                    all_data.append({
                        'type': 'question',
                        'title': item.get('title', ''),
                        'body': item.get('body', ''),
                        'score': item.get('score', 0),
                        'created_date': dt.fromtimestamp(item.get('creation_date', 0)).date(),
                        'tags': item.get('tags', [])
                    })
            
            # Conservative rate limiting
            time.sleep(1.0)  # 1 second between requests
            
        except requests.RequestException as e:
            if "429" in str(e):
                print(f"Rate limit hit on questions page {page}. Waiting 120 seconds...")
                time.sleep(120)  # Wait 2 minutes when rate limited
            else:
                print(f"Error fetching questions page {page}: {e}")
            continue
    
    return all_data

def clean_text(text):
    """
    Clean HTML tags and special characters from text
    """
    import re
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-\:]', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_sentiment(text):
    """
    Analyze sentiment of text using TextBlob
    """
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return 'positive'
    elif polarity < -0.1:
        return 'negative'
    else:
        return 'neutral'

def check_tag_exists(tag):
    """
    Check if a tag exists on Stack Overflow
    """
    url = f"{BASE_URL}/tags"
    params = {
        'inname': tag,
        'site': SITE,
        'pagesize': 1
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'items' in data and data['items']:
            return True, data['items'][0].get('count', 0)
        return False, 0
    except requests.RequestException as e:
        print(f"Error checking tag: {e}")
        return False, 0

def main():
    # --- Configuration ---
    tag = 'auth0'  # Change this to any tag you want to analyze
    pages = 5  # Number of pages to fetch (each page has 100 items) - increased to get more data
    
    print(f"Checking if tag '{tag}' exists on Stack Overflow...")
    tag_exists, tag_count = check_tag_exists(tag)
    
    if not tag_exists:
        print(f"Tag '{tag}' not found on Stack Overflow.")
        print("Trying with 'authentication' tag instead...")
        tag = 'authentication'
        tag_exists, tag_count = check_tag_exists(tag)
        if not tag_exists:
            print("Using 'python' tag as fallback...")
            tag = 'python'
            tag_exists, tag_count = check_tag_exists(tag)
    
    print(f"Using tag: {tag} (found {tag_count} posts)")
    print(f"Fetching Stack Overflow data for tag: {tag}")
    print("This may take a few minutes due to API rate limiting...")
    
    # Fetch data from Stack Overflow
    data = fetch_stackoverflow_data(tag, pages=pages)
    
    if not data:
        print('No data found for the specified tag.')
        return
    
    print(f"Fetched {len(data)} items from Stack Overflow")
    
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
    plt.title(f'Sentiment Analysis of Stack Overflow {tag} Posts by Month (100% Stacked)')
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
    
    # Save raw data to CSV
    csv_filename = f"stackoverflow_{tag}_sentiment_data.csv"
    df.to_csv(csv_filename, index=False)
    print(f"\n=== Raw Data Saved ===")
    print(f"Complete dataset saved to: {csv_filename}")
    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")

if __name__ == "__main__":
    main()
