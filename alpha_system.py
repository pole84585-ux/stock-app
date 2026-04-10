import akshare as ak
import pandas as pd
import numpy as np
import requests

# =========================
# 股票池（可扩展）
# =========================
stocks = ["600519", "600036", "601318", "000001", "000858", "300750"]

capital = 100000

# =========================
# 推送
# =========================
def send_telegram(msg):
    token = "YOUR_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

# =========================
# 因子计算🔥
# =========================
def get_score(df):
    df["ret"] = df["收盘"].pct_change()
    df["ma5"] = df["收盘"].rolling(5).mean()
    df["ma20"] = df["收盘"].rolling(20).mean()
    df["vol_ma"] = df["成交量"].rolling(5).mean()

    latest = df.iloc[-1]

    score = 0

    # 趋势
    if latest["ma5"] > latest["ma20"]:
        score += 30

    # 动量
    if latest["ret"] > 0:
        score += 20

    # 放量
    if latest["成交量"] > latest["vol_ma"]:
        score += 20

    # 强势突破
    if latest["收盘"] == df["收盘"].max():
        score += 30

    return score

# =========================
# 主逻辑
# =========================
results = []
msg = "📊 A股增强收益系统\n\n"

for s in stocks:
    try:
        df = ak.stock_zh_a_hist(symbol=s, period="daily", adjust="qfq")
        df = df.tail(60)

        score = get_score(df)

        # =========================
        # 动态仓位🔥
        # =========================
        if score >= 80:
            position = 0.3
            signal = "🔥强买"
        elif score >= 60:
            position = 0.15
            signal = "🟡观察"
        else:
            position = 0

        latest_price = df.iloc[-1]["收盘"]

        results.append((s, score, signal, position))

        msg += f"{s} | 分数:{score} | {signal} | 仓位:{position}\n"

    except:
        continue

# =========================
# 输出信号
# =========================
print(msg)

# =========================
# 推送
# =========================
send_telegram(msg)
