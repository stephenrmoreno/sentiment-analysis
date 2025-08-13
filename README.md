# Twitter Sentiment Analysis: Auth0

This project fetches tweets about "Auth0" and performs sentiment analysis using Python.

## Setup

1. Clone this repository or copy the files to your local machine.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your Twitter Developer credentials (API key, API secret, Access token, Access token secret).

## Usage

1. Edit `twitter_sentiment.py` to add your Twitter API credentials.
2. Run the script:
   ```bash
   python twitter_sentiment.py
   ```

The script will fetch recent tweets about "Auth0", analyze their sentiment, and display a summary plot. 