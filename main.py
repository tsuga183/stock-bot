import yfinance as yf
import requests
import os
import time

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

TICKERS = [
    "7203","6758","9984","8306","9432",
    "7974","6861","6501","6098","4063"
]

def send(msg):
    try:
        requests.post(WEBHOOK_URL, json={"content": msg})
    except:
        print("Discord送信失敗")


# 🔥 安定取得（超重要）
def fetch_data(ticker):
    for i in range(3):  # 最大3回リトライ
        try:
            df = yf.download(
                f"{ticker}.T",
                period="6mo",
                progress=False,
                threads=False  # ← 安定化ポイント
            )

            if df is not None and not df.empty:
                return df

        except Exception as e:
            print(f"{ticker} retry {i+1}")

        time.sleep(2)

    return None


def get_score(ticker):
    df = fetch_data(ticker)

    if df is None or len(df) < 50:
        return None

    score = 0

    # 超シンプルロジック（まず動かす）
    if df["Close"].iloc[-1] > df["Close"].iloc[-5]:
        score += 10

    if df["Close"].iloc[-1] > df["Close"].mean():
        score += 10

    if df["Volume"].iloc[-1] > df["Volume"].mean():
        score += 10

    return score


results = []
debug = "【全銘柄】\n"

for t in TICKERS:
    s = get_score(t)

    if s is None:
        debug += f"{t}: NG\n"
    else:
        debug += f"{t}: {s}\n"
        if s >= 10:
            results.append((t, s))

send(debug)

if results:
    results.sort(key=lambda x: x[1], reverse=True)

    msg = "【ヒット銘柄】\n"
    for r in results:
        msg += f"{r[0]} スコア:{r[1]}\n"
else:
    msg = "ヒットなし"

send(msg)
send("テストOK")