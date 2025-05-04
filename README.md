# 📈 TSX News-Based Stock Recommendation System

This Python script scrapes recent press releases from PR Newswire, extracts relevant TSX stock symbols from the articles, retrieves their recent stock data via Yahoo Finance, and provides visualizations and recommendations on whether to buy, wait, or avoid the stock based on recent trends.

## 🧠 Features

Scrapes up to 100 pages of recent PR news articles.

Extracts stock symbols using a custom regex filter.

Filters to a set of relevant industry symbols.

Pulls 30-day historical stock data from Yahoo Finance.

Visualizes stock price and volume trends.

Generates automated buy/wait/sell recommendations.

Saves all outputs (news, plots, recommendations) to disk.

📦 Dependencies
Install required packages via pip:

```
pip install requests beautifulsoup4 pandas numpy yfinance matplotlib seaborn
```

## Outputs:

parsed_news.csv: All relevant news articles.

<SYMBOL>_30day_data.csv: 30-day stock data for each symbol.

<SYMBOL>_30day_trend.png: Visualization of price and volume trends.

<SYMBOL>_recommendation.txt: Text-based recommendation summary.

## 🔍 Recommendation Logic
### Uses linear regression and percentage change over 30 days:

📈 Buy: if trend is positive and price increased >2%

🕒 Wait: if movement is minimal

📉 Do Not Buy: if trend is negative and price dropped >2%

## 📁 Project Structure

```
project.py                # Main script
README.md                 # This file
*.csv                     # Output stock and news data
*.png                     # Stock trend plots
*_recommendation.txt      # Stock recommendations
```
