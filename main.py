import yfinance as yf
import requests
import os

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

def get_all_tickers():
    # 確実に取得できる銘柄
    return ["7203", "6758", "9984", "8306", "9432"]

TICKERS = get_all_tickers()

def send_discord(msg):
    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"content": msg})
    else:
        print("Webhook未設定")

def get_score(ticker):
    try:
        df = yf.download(f"{ticker}.T", period="6mo", progress=False)
        print(f"{ticker} empty={df.empty} len={len(df)}")
    except Exception as e:
        print(f"取得失敗: {ticker} {e}")
        return 0

    if df.empty or len(df) < 75:
        return 0

    df["MA25"] = df["Close"].rolling(25).mean()
    df["MA75"] = df["Close"].rolling(75).mean()
    df["Vol_avg"] = df["Volume"].rolling(25).mean()

    df["Vol_ratio"] = df["Volume"] / df["Vol_avg"]
    df["High60"] = df["High"].rolling(60).max()

    score = 0

    # めちゃゆる条件（とりあえず出す用）
    if df["MA25"].iloc[-1] > df["MA75"].iloc[-1]:
        score += 20

    if df["Close"].iloc[-1] >= df["High60"].iloc[-1] * 0.85:
        score += 20

    if df["Vol_ratio"].iloc[-1] >= 0.8:
        score += 20

    print(f"{ticker} score={score}")

    return score


results = []

for t in TICKERS:
    try:
        s = get_score(t)
        results.append((t, s))  # ← 条件なしで全部入れる（重要）
    except Exception as e:
        print(f"スキップ: {t} {e}")
        continue

# スコア順に並び替え
results = sorted(results, key=lambda x: x[1], reverse=True)

# 上位だけ表示（見やすく）
msg = "【銘柄スコア一覧】\n"
for r in results:
    msg += f"{r[0]} スコア:{r[1]}\n"

send_discord(msg)

# テスト
send_discord("テスト送信")