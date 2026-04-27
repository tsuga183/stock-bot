import yfinance as yf
import requests
import os

WEBHOOK_URL = "https://discord.com/api/webhooks/1498252515525918740/n9DVZv19ChCI76ki4KJD8Gd6-lD1dQIN9WzVpBZ5T6u1x4YbS5_Rjwip4hakQKMpbhNt"

TICKERS = ["3445", "6526", "6963"]

def send_discord(msg):
    requests.post(WEBHOOK_URL, json={"content": msg})

def get_score(ticker):
    df = yf.download(f"{ticker}.T", period="6mo")
    
    df["MA25"] = df["Close"].rolling(25).mean()
    df["MA75"] = df["Close"].rolling(75).mean()
    df["Vol_avg"] = df["Volume"].rolling(25).mean()
    df["Vol_ratio"] = df["Volume"] / df["Vol_avg"]
    df["High60"] = df["High"].rolling(60).max()
    
    score = 0
    
    if df["MA25"].iloc[-1] > df["MA75"].iloc[-1]:
        score += 20
        
    if df["Close"].iloc[-1] >= df["High60"].iloc[-1] * 0.97:
        score += 20
        
    if 1.2 <= df["Vol_ratio"].iloc[-1] <= 2.0:
        score += 20
        
    return score

results = []

for t in TICKERS:
    try:
        s = get_score(t)
        if s >= 60:
            results.append((t, s))
    except:
        pass

if results:
    msg = "【銘柄抽出】\n"
    for r in results:
        msg += f"{r[0]} スコア:{r[1]}\n"
    
    send_discord(msg)
