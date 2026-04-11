import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="量化系统", layout="wide")

st.title("📊 V3稳定赚钱系统")

# =========================
# 显示收益
# =========================
if os.path.exists("equity.csv"):
    df_eq = pd.read_csv("equity.csv")
    current = df_eq["value"].iloc[-1]
    start = df_eq["value"].iloc[0]

    ret = (current / start - 1) * 100

    st.metric("💰当前资金", round(current,2))
    st.metric("📈累计收益%", round(ret,2))
else:
    st.warning("暂无收益数据")

# =========================
# 显示最近信号（简单版）
# =========================
st.subheader("📌 使用说明")

st.markdown("""
### 🟢 操作规则
- 🔥买入：最多20%仓位
- 🟡观察：等待回调
- ❌不做：跳过

### ⚠ 风控
- 单票亏损5%必须卖
- 不满仓
""")
