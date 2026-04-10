import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="A股量化系统", layout="wide")

st.title("📊 手机可用量化选股系统（无数据文件版）")

# =========================
# 1. 自动生成模拟数据
# =========================
np.random.seed(42)

stocks = [
    "000001.SZ","000002.SZ","600036.SH","600519.SH",
    "000858.SZ","300750.SZ","002594.SZ","601318.SH",
    "601166.SH","000333.SZ"
]

df = pd.DataFrame({
    "code": stocks,
    "close": np.random.uniform(10, 200, len(stocks)),
    "vol": np.random.uniform(10000, 100000, len(stocks)),
    "pct": np.random.uniform(-3, 5, len(stocks))
})

# =========================
# 2. 多因子模型
# =========================
df["vol_score"] = df["vol"] / df["vol"].mean()
df["momentum"] = df["pct"] / (abs(df["pct"].mean()) + 1e-6)

df["score"] = (df["vol_score"] + df["momentum"]) * 50

# =========================
# 3. 排序选股
# =========================
result = df.sort_values("score", ascending=False)

st.subheader("🔥 今日推荐股票")

for _, row in result.iterrows():
    st.markdown(f"""
### 🥇 {row['code']}
- 💰 价格：{row['close']:.2f}
- 📊 成交量：{int(row['vol'])}
- 📈 涨跌：{row['pct']:.2f}%
- ⭐ 评分：{row['score']:.2f}
""")

# =========================
# 4. 热点提示（简化版）
# =========================
st.subheader("🔥 市场状态")

avg_pct = df["pct"].mean()

if avg_pct > 1:
    st.success("市场偏强：适合做多")
elif avg_pct < -1:
    st.error("市场偏弱：建议空仓/防守")
else:
    st.warning("市场震荡：轻仓操作")

st.markdown("---")
st.info("📌 手机可直接打开使用（无数据文件/无API限制）")
