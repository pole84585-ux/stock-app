import streamlit as st
import akshare as ak
import pandas as pd
import numpy as np
import requests

st.set_page_config(page_title="V3+V4终极交易系统", layout="wide")

st.title("🔥 V3+V4融合终极版（信号+回测+风控）")

# =========================
# 股票池
# =========================
stocks = ["600519", "600036", "601318", "000001", "000858", "300750"]

# =========================
# 获取历史数据
# =========================
def get_data(code):
    df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
    df = df.tail(200)

    df["ret"] = df["收盘"].pct_change()
    df["vol"] = df["成交量"]
    df["vol_chg"] = df["vol"].pct_change()

    return df.dropna()

# =========================
# 回测系统（V4核心🔥）
# =========================
def backtest(df):
    df["signal"] = (df["ret"] > 0) & (df["vol_chg"] > 0.2)

    trades = df[df["signal"]]

    win_rate = (trades["ret"] > 0).mean()
    avg_return = trades["ret"].mean()

    # 模拟资金曲线
    capital = 100000
    equity = capital * (1 + trades["ret"]).cumprod()

    if len(equity) > 0:
        drawdown = (equity - equity.cummax()) / equity.cummax()
        max_dd = drawdown.min()
    else:
        max_dd = 0

    return win_rate, avg_return, max_dd

# =========================
# 北向资金
# =========================
def north_money():
    try:
        df = ak.stock_hsgt_north_net_flow_in_em()
        latest = df.iloc[-1]
        return latest["沪深港通:北向资金:当日净流入"]
    except:
        return 0

north = north_money()

# =========================
# 主逻辑
# =========================
results = []

for s in stocks:
    try:
        df = get_data(s)

        # ===== 回测 =====
        win_rate, avg_return, max_dd = backtest(df)

        # ===== 当前信号 =====
        latest = df.iloc[-1]

        score = 0

        if latest["ret"] > 0:
            score += 1
        if latest["vol_chg"] > 0.2:
            score += 1

        signal = "不做"
        position = 0

        # 🔥 核心过滤（历史 + 当前）
        if score == 2 and win_rate > 0.55:
            signal = "🔥 可买（通过回测）"
            position = 0.2
        elif score == 2:
            signal = "⚠️ 信号强但历史差"

        results.append({
            "股票": s,
            "胜率": round(win_rate*100,1),
            "平均收益": round(avg_return*100,2),
            "最大回撤": round(max_dd*100,2),
            "信号": signal,
            "仓位": f"{position*100:.0f}%"
        })

    except:
        continue

df_result = pd.DataFrame(results)

# =========================
# 输出
# =========================

st.subheader("💰 北向资金")
st.write("净流入：", north)

st.subheader("📊 策略验证 + 今日信号")
st.dataframe(df_result)

# =========================
# 筛选可交易
# =========================
st.subheader("🔥 今日可交易（已过滤）")

buy = df_result[df_result["信号"].str.contains("可买")]

st.dataframe(buy)

# =========================
# 推送
# =========================
def send_telegram(msg):
    token = "YOUR_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

if st.button("📡 推送今日交易"):

    msg = "📊 今日交易信号（V3+V4）\n\n"

    for _, row in buy.iterrows():
        msg += f"{row['股票']} 胜率{row['胜率']}% 仓位{row['仓位']}\n"

    send_telegram(msg)

    st.success("已推送")
