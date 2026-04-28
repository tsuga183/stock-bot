import yfinance as yf
import requests
import os

WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# 実在する銘柄に変更（超重要）
def get_all_tickers():
    return [
        "7203",  # トヨタ
        "6758",  # ソニー
        "9984",  # ソフトバンク
        "8306",  # 三菱UFJ
        "9432",  # NTT
        "7974",  # 任天堂
        "6861",  # キーエンス
        "6501",  # 日立
        "6098",  # リクルート
        "4063",  # 信越化学
    ]

TICKERS = get_all_tickers()

def send_discord(msg):
    requests.post(WEBHOOK_URL, json={"content": msg})

def get_score(ticker):
    try:
        df = yf.download(f"{ticker}.T", period="6mo", progress=False)
    except:
        return -1  # エラー区別

    if df.empty or len(df) < 75:
        return -1

    df["MA25"] = df["Close"].rolling(25).mean()
    df["MA75"] = df["Close"].rolling(75).mean()
    df["Vol_avg"] = df["Volume"].rolling(25).mean()
    df["Vol_ratio"] = df["Volume"] / df["Vol_avg"]
    df["High60"] = df["High"].rolling(60).max()

    score = 0

    if df["MA25"].iloc[-1] > df["MA75"].iloc[-1]:
        score += 20

    if df["Close"].iloc[-1] >= df["High60"].iloc[-1] * 0.95:
        score += 20

    if df["Vol_ratio"].iloc[-1] >= 1.1:
        score += 20

    return score


results = []
debug_msg = "【全銘柄スコア】\n"

for t in TICKERS:
    s = get_score(t)

    if s == -1:
        debug_msg += f"{t}: データ取得NG\n"
    else:
        debug_msg += f"{t}: {s}\n"

        if s >= 20:
            results.append((t, s))

send_discord(debug_msg)

if results:
    msg = "【抽出銘柄】\n"
    for r in results:
        msg += f"{r[0]} スコア:{r[1]}\n"
else:
    msg = "銘柄なし（条件未達）"

send_discord(msg)

send_discord("テスト送信")