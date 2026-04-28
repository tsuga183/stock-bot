import yfinance as yf
import requests
import os

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

def get_all_tickers():
    # 確実にデータ取れる銘柄だけ
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
        print(f"{ticker} empty={df.empty} len={len(df)}")  # デバッグ
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

    # ゆるめ条件
    if df["MA25"].iloc[-1] > df["MA75"].iloc[-1]:
        score += 20

    if df["Close"].iloc[-1] >= df["High60"].iloc[-1] * 0.90:
        score += 20

    if 1.0 <= df["Vol_ratio"].iloc[-1] <= 3.0:
        score += 20

    print(f"{ticker} score={score}")  # デバッグ

    return score


results = []

for t in TICKERS:
    try:
        s = get_score(t)
        if s >= 40:
            results.append((t, s))
    except Exception as e:
        print(f"スキップ: {t} {e}")
        continue

# 結果送信
if results:
    msg = "【銘柄抽出】\n"
    for r in results:
        msg += f"{r[0]} スコア:{r[1]}\n"
    send_discord(msg)
else:
    send_discord("銘柄なし（条件未達 or データ取得NG）")

# テスト
send_discord("テスト送信")