import tweepy
import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt
import datetime

# --- Twitter API credentials (replace with your own) ---
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAIUW2wEAAAAAdi3r00oigbT3xCX6SgJiYJ%2FrWLM%3D66dJgffnywtvilBvgNBK1Yp8GelAFa32jdPmV5vp1DkbW7az5C'

# --- Authenticate with Twitter API v2 ---
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# --- Fetch Tweets about 'Auth0' ---
query = 'Auth0 -is:retweet lang:en'
tweet_count = 100

response = client.search_recent_tweets(query=query, max_results=100, tweet_fields=['text', 'created_at'])
tweets = getattr(response, 'data', None) or []

if not tweets:
    print('No tweets found for the query.')
    exit()

# Extract text and date
data = [{'tweet': tweet.text, 'date': tweet.created_at.date() if hasattr(tweet, 'created_at') and tweet.created_at else datetime.date.today()} for tweet in tweets]
df = pd.DataFrame(data)

# Add workweek column (year-week)
df['workweek'] = df['date'].apply(lambda d: f"{d.isocalendar().year}-W{d.isocalendar().week:02d}")

# --- Sentiment Analysis ---
def get_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity  # type: ignore
    if polarity > 0:
        return 'positive'
    elif polarity == 0:
        return 'neutral'
    else:
        return 'negative'

df['sentiment'] = df['tweet'].apply(get_sentiment)

# Group by date and sentiment, count tweets
counts = df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)

# Normalize to 100% stacked (percentage per day)
percentages = counts.div(counts.sum(axis=1), axis=0) * 100

# Plot 100% stacked bar chart
percentages.plot(kind='bar', stacked=True, color=['green', 'blue', 'red'])
plt.title('Sentiment Analysis of Tweets about Auth0 by Day (100% Stacked)')
plt.xlabel('Date')
plt.ylabel('Percentage of Tweets (%)')
plt.legend(title='Sentiment')
plt.tight_layout()
plt.show()

# --- Print a sample of results ---
print(df.head()) 