import yfinance as yf
import requests
import os
import traceback

print("=== START ===")

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
print("Webhook:", WEBHOOK_URL)

def send_discord(msg):
    print(">>> send_discord called")
    print(">>> URL:", WEBHOOK_URL)

    if not WEBHOOK_URL:
        print(">>> ERROR: WEBHOOK_URL is None")
        return

    try:
        res = requests.post(WEBHOOK_URL, json={"content": msg})
        print(">>> status:", res.status_code)
        print(">>> response:", res.text)
    except Exception as e:
        print(">>> send_discord ERROR:", e)
        traceback.print_exc()


def get_all_tickers():
    return [str(i) for i in range(3000, 3050)]

TICKERS = get_all_tickers()


def get_score(ticker):
    print(f"--- {ticker} start ---")

    try:
        df = yf.download(f"{ticker}.T", period="6mo", progress=False)
        print(f"{ticker}: download done len={len(df)}")
    except Exception as e:
        print(f"取得失敗: {ticker} {e}")
        traceback.print_exc()
        return 0

    if df is None or df.empty or len(df) < 75:
        print(f"{ticker}: データ不足")
        return 0

    try:
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

        print(f"{ticker}: score={score}")
        return score

    except Exception as e:
        print(f"計算エラー: {ticker} {e}")
        traceback.print_exc()
        return 0


print("=== LOOP START ===")

results = []

for t in TICKERS:
    print(f"processing: {t}")
    s = get_score(t)

    if s >= 60:
        results.append((t, s))

print("=== LOOP END ===")
print("results:", results)


if results:
    msg = "【銘柄抽出】\n"
    for r in results:
        msg += f"{r[0]} スコア:{r[1]}\n"

    send_discord(msg)

# 最後に必ず送るテスト
send_discord("テスト送信")