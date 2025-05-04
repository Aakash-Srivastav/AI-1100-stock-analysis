import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import yfinance as yf
import re
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

def get_news(days_back=14, pages_to_check=100):
    base_url = "https://www.prnewswire.com/news-releases/news-releases-list/"

    today = datetime.now()
    cutoff_date = today - timedelta(days=days_back)

    articles = []

    for page in range(1, pages_to_check+1):
        url = f"{base_url}?page={page}&pagesize=25"
        print(f"Scraping page {page}...")
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        news_links = soup.select("div.card")

        for link_data in news_links:
            try:
                sub_link = link_data.find("a").get("href")
            except:
                continue
            
            link = "https://www.prnewswire.com" + sub_link

            # Get article content
            article_res = requests.get(link)
            article_soup = BeautifulSoup(article_res.text, "html.parser")

            date_span = article_soup.find(class_="mb-no").get_text()
            clean_date_span = date_span.replace(" ET", "")
            article_dt = datetime.strptime(clean_date_span, "%b %d, %Y, %H:%M")
            if article_dt< cutoff_date:
                continue

            title = article_soup.find("h1").get_text().split("\n")[0]

            body = article_soup.find("div", class_="col-lg-10 col-lg-offset-1")
            try:
                content = body.get_text(separator=" ", strip=True)
            except:
                continue

            articles.append({
                "title": title,
                "date": article_dt.strftime("%Y-%m-%d"),
                "link": link,
                "content": content
            })
    return pd.DataFrame(articles)

def extract_symbols(df, industry_symbols):
    symbol_pattern = r"\(TSX:\s*([A-Z]+)\)"
    matches = []
    for _, row in df.iterrows():
        found = re.findall(symbol_pattern, row['content'])
        filtered = [sym for sym in found if sym in industry_symbols]
        if filtered:
            matches.append((row['title'], filtered[:3]))  # max 3 per article

    return list({sym for _, symbols in matches for sym in symbols})
    #     if found:
    #         matches.append(found)
    # return matches

# 3. Get Yahoo Finance Data
def get_yahoo_data(symbol):
    ticker = yf.Ticker(symbol + ".TO")  # TSX symbols end in .TO
    hist = ticker.history(period="30d")
    hist.reset_index(inplace=True)
    hist['Symbol'] = symbol
    return hist

# 4. Visualize
def visualize_stock(df, symbol):
    sns.set(style="whitegrid")
    fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    sns.lineplot(data=df, x='Date', y='Volume', ax=axs[0], color='blue')
    axs[0].set_title(f'{symbol} - Volume (30 Days)', fontsize=14)

    sns.lineplot(data=df, x='Date', y='Close', ax=axs[1], color='green')
    axs[1].set_title(f'{symbol} - Daily Close Price (30 Days)', fontsize=14)

    plt.tight_layout()
    plt.savefig(f'{symbol}_30day_trend.png')
    plt.close()
    print(f"Saved graph as {symbol}_30day_trend.png")

# # 5. Recommend
# def make_recommendation(df, symbol):
#     first = df['Close'].iloc[0]
#     last = df['Close'].iloc[-1]

#     trend = "inconsistent"
#     if last > first * 1.05:
#         trend = "upward"
#         msg = f"BUY STOCK! ({symbol})"
#     elif last < first * 0.95:
#         trend = "downward"
#         msg = f"DO NOT BUY STOCK! ({symbol})"
#     else:
#         msg = f"WAIT BEFORE BUYING STOCK! ({symbol})"

#     print(f"Trend: {trend} | Recommendation: {msg}")
#     return msg

def make_recommendation(symbol, df):
    closes = df['Close'].values
    x = np.arange(len(closes))
    slope = np.polyfit(x, closes, 1)[0]
    pct_change = ((closes[-1] - closes[0]) / closes[0]) * 100

    if slope > 0 and pct_change > 2:
        msg = "BUY STOCK!"
    elif slope < 0 and pct_change < -2:
        msg = "NOT BUY STOCK!"
    else:
        msg = "WAIT BEFORE BUYING STOCK!"

    print(f"{symbol} Recommendation: {msg} ({pct_change:.2f}%)")
    
    with open(f"{symbol}_recommendation.txt", "w") as f:
        f.write(f"Stock: {symbol}\n")
        f.write(f"Start Price: ${closes[0]:.2f}\n")
        f.write(f"End Price: ${closes[-1]:.2f}\n")
        f.write(f"Change: {pct_change:.2f}%\n")
        f.write(f"Slope: {slope:.4f}\n")
        f.write(f"Recommendation: {msg}\n")
    
    return msg

if __name__ == "__main__":
    print("Fetching recent news...")
    news_df = get_news()
    news_df.to_csv("parsed_news.csv", index=False)

    print("Extracting symbols...")

    industry_symbols = ['IAU','NGD','OGC','ARIS']
    found_symbols = extract_symbols(news_df, industry_symbols)
    print(f"Found symbols in news: {found_symbols}")

    if not found_symbols:
        print("No relevant stock symbols found in recent news.")
    else:
        for elem in range(len(found_symbols)):
            symbol_to_review = found_symbols[elem]
            print(f"Analyzing stock: {symbol_to_review}")

            stock_df = get_yahoo_data(symbol_to_review)
            visualize_stock(stock_df, symbol_to_review)
            recommendation = make_recommendation(symbol_to_review, stock_df)

            # Save data + recommendation
            stock_df.to_csv(f"{symbol_to_review}_30day_data.csv", index=False)
            # with open(f"{symbol_to_review}_recommendation.txt", "w") as f:
            #     f.write(recommendation)

