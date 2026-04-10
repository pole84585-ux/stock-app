import streamlit as st
import pandas as pd

st.set_page_config(page_title="A股量化选股系统", layout="wide")

st.title("📊 A股量化选股系统（稳定版）")

# =========================
# 读取数据
# =========================
df = pd.read_csv("data.csv")

df = df.dropna()

# =========================
# 因子模型
# =========================
df["vol_score"] = df["vol"] / df["vol"].mean()
df["momentum"] = df["pct"] / (abs(df["pct"].mean()) + 1e-6)

df["score"] = (df["vol_score"] + df["momentum"]) * 50

# =========================
# 排序选股
# =========================
result = df.sort_values("score", ascending=False).head(10)

st.subheader("🔥 今日推荐")

for _, row in result.iterrows():
    st.markdown(f"""
    ### {row['code']}
    - 📊 评分：{row['score']:.2f}
    - 💰 收盘价：{row['close']}
    - 📦 成交量：{row['vol']}
    - 📈 涨跌：{row['pct']}%
    """)

st.markdown("---")
st.info("📌 数据来自本地 data.csv（已脱离API）")
