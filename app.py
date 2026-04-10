import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime

st.set_page_config(page_title="V3+稳定交易系统", layout="wide")

st.title("🔥 V3+稳定版（资金 + 回测 + 自动交易）")

# =========================
# 读取本地数据（稳定核心🔥）
# =========================
try:
    df_all = pd.read_csv("data.csv")
except:
    st.error("❌ 没有数据，请先运行 data_update.py")
    st.stop()

# =========================
# 股票池
# =========================
stocks = df_all["code"].unique()

# =========================
# 获取单只股票数据
# =========================
def get_data(code):
    df = df_all[df_all["code"] == code].copy()
    return df.dropna()

# =========================
# 回测系统（V4核心🔥）
# =========================
def backtest(df):
    df["signal"] = (df["ret"] > 0) & (df["vol_chg"] > 0.2)

    trades = df[df["signal"]]

    if len(trades) == 0:
        return 0, 0, 0

    win_rate = (trades["ret"] > 0).mean()
    avg_return = trades["ret"].mean()

    equity = (1 + trades["ret"]).cumprod()

    drawdown = (equity - equity.cummax()) / equity.cummax()
    max_dd = drawdown.min()

    return win_rate, avg_return, max_dd

# =========================
# 北向资金趋势判断🔥
# =========================
try:
    north_df = pd.read_csv("north.csv")

    flows = north_df["沪深港通:北向资金:当日净流入"].tail(3)

    if all(flows > 0):
        north_trend = "🟢 连续流入（强势）"
    elif all(flows < 0):
        north_trend = "🔴 连续流出（风险）"
    else:
        north_trend = "🟡 震荡"

    north_value = flows.iloc[-1]

except:
    north_trend = "未知"
    north_value = 0

# =========================
# 主逻辑
# =========================
results = []

for s in stocks:
    try:
        df = get_data(s)

        if df.empty:
            continue

        win_rate, avg_return, max_dd = backtest(df)

        latest = df.iloc[-1]

        score = 0

        if latest["ret"] > 0:
            score += 1
        if latest["vol_chg"] > 0.2:
            score += 1

        signal = "不做"
        position = 0

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

    except Exception as e:
        st.warning(f"{s} 出错: {e}")

df_result = pd.DataFrame(results)

# =========================
# 防止空数据崩溃
# =========================
if df_result.empty:
    st.error("❌ 没有可用数据")
    st.stop()

# =========================
# 页面显示
# =========================

st.subheader("💰 北向资金（聪明钱）")
st.write("今日流入：", north_value)
st.write("趋势：", north_trend)

st.subheader("📊 策略验证 + 今日信号")
st.dataframe(df_result)

# =========================
# 自动交易清单🔥
# =========================
st.subheader("🔥 今日交易清单（自动生成）")

if "信号" in df_result.columns:
    trade_list = df_result[
        (df_result["信号"].str.contains("可买")) &
        (df_result["胜率"] > 55)
    ]
else:
    trade_list = pd.DataFrame()

if trade_list.empty:
    st.warning("⚠️ 今日没有符合条件的股票")
else:
    for _, row in trade_list.iterrows():
        st.success(f"""
🟢 股票：{row['股票']}
- 胜率：{row['胜率']}%
- 仓位：{row['仓位']}
""")

# =========================
# Telegram 推送
# =========================
def send_telegram(msg):
    token = "YOUR_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": msg})

# =========================
# 自动推送（每天一次）
# =========================
now = datetime.datetime.now()

if now.hour == 9:
    if not trade_list.empty:
        msg = "📊 今日交易清单\n\n"

        for _, row in trade_list.iterrows():
            msg += f"{row['股票']} 胜率{row['胜率']}% 仓位{row['仓位']}\n"

        send_telegram(msg)

# =========================
# 手动推送按钮（备用）
# =========================
if st.button("📡 手动推送"):
    if trade_list.empty:
        st.warning("没有可推送内容")
    else:
        msg = "📊 今日交易清单\n\n"

        for _, row in trade_list.iterrows():
            msg += f"{row['股票']} 胜率{row['胜率']}% 仓位{row['仓位']}\n"

        send_telegram(msg)
        st.success("✅ 已推送到手机")
