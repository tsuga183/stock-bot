import yfinance as yf
import requests
import os

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

def send_discord(msg):
    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"content": msg})
    print(msg)

TICKERS = ["7203", "6758", "9984", "8306", "9432"]

results = []

for t in TICKERS:
    try:
        df = yf.download(f"{t}.T", period="6mo", progress=False)

        print(f"{t} → データ件数: {len(df)}")

        if df.empty:
            send_discord(f"{t} データ取得NG")
            continue

        # 最低限スコア
        score = len(df)

        send_discord(f"{t} OK データ数:{len(df)}")

        results.append((t, score))

    except Exception as e:
        send_discord(f"{t} エラー: {e}")

if results:
    msg = "【データ取得確認】\n"
    for r in results:
        msg += f"{r[0]} → {r[1]}\n"
else:
    msg = "全銘柄データ取得NG"

send_discord(msg)