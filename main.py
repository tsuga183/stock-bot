import yfinance as yf
import requests
import os

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

def get_all_tickers():
    return [str(i) for i in range(3000, 3050)]

TICKERS = get_all_tickers()

def send_discord(msg):
    requests.post(WEBHOOK_URL, json={"content": msg})

def get_score(ticker):
    try:
        df = yf.download(f"{ticker}.T", period="6mo", progress=False)
    except Exception as e:
        return 0

    if df.empty or len(df) < 75:
        return 0

    df["MA25"] = df["Close"].rolling(25).mean()
    df["MA75"] = df["Close"].rolling(75).mean()
    df["Vol_avg"] = df["Volume"].rolling(25).mean()
    df["Vol_ratio"] = df["Volume"] / df["Vol_avg"]
    df["High60"] = df["High"].rolling(60).max()

    score = 0

    # 条件① ゴールデンクロス気味
    if df["MA25"].iloc[-1] > df["MA75"].iloc[-1]:
        score += 20

    # 条件② 高値付近
    if df["Close"].iloc[-1] >= df["High60"].iloc[-1] * 0.95:
        score += 20

    # 条件③ 出来高増
    if df["Vol_ratio"].iloc[-1] >= 1.1:
        score += 20

    return score


results = []
debug_msg = "【全銘柄スコア】\n"

for t in TICKERS:
    try:
        s = get_score(t)
        debug_msg += f"{t}: {s}\n"

        if s >= 20:  # ←ゆるめ条件
            results.append((t, s))

    except Exception:
        debug_msg += f"{t}: エラー\n"

# デバッグ送信
send_discord(debug_msg)

# 抽出結果
if results:
    msg = "【銘柄スコア一覧】\n"
    for r in results:
        msg += f"{r[0]} スコア:{r[1]}\n"
else:
    msg = "銘柄なし（条件未達）"

send_discord(msg)

# テスト確認
send_discord("テスト送信")