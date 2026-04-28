import yfinance as yf
import requests
import os

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# ✅ 実在する銘柄（まずは安定動作優先）
TICKERS = [
    "7203", "6758", "9984", "8306", "9432",
    "7974", "6861", "6501", "6098", "4063"
]

def send_discord(msg):
    requests.post(WEBHOOK_URL, json={"content": msg})


def get_score(ticker):
    try:
        df = yf.download(f"{ticker}.T", period="6mo", progress=False)
    except Exception:
        return None  # エラー

    if df is None or df.empty or len(df) < 75:
        return None

    df["MA25"] = df["Close"].rolling(25).mean()
    df["MA75"] = df["Close"].rolling(75).mean()
    df["Vol_avg"] = df["Volume"].rolling(25).mean()
    df["Vol_ratio"] = df["Volume"] / df["Vol_avg"]
    df["High60"] = df["High"].rolling(60).max()

    score = 0

    # 条件①
    if df["MA25"].iloc[-1] > df["MA75"].iloc[-1]:
        score += 20

    # 条件②（少し緩め）
    if df["Close"].iloc[-1] >= df["High60"].iloc[-1] * 0.93:
        score += 20

    # 条件③（少し緩め）
    if df["Vol_ratio"].iloc[-1] >= 1.05:
        score += 20

    return score


results = []
debug_msg = "【全銘柄スコア】\n"

for t in TICKERS:
    s = get_score(t)

    if s is None:
        debug_msg += f"{t}: データ取得NG\n"
    else:
        debug_msg += f"{t}: {s}\n"

        if s >= 20:  # ←ここ緩め（検出しやすく）
            results.append((t, s))

# デバッグ表示
send_discord(debug_msg)

# 抽出結果
if results:
    # スコア順に並べる
    results.sort(key=lambda x: x[1], reverse=True)

    msg = "【抽出銘柄ランキング】\n"
    for r in results:
        msg += f"{r[0]} スコア:{r[1]}\n"
else:
    msg = "銘柄なし（条件未達）"

send_discord(msg)

# 確認用
send_discord("テスト送信OK")