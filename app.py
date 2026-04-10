import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="V2量化系统", layout="wide")

st.title("📊 V2专业量化系统（无Tushare版）")

# =========================
# 免费实时数据源（新浪接口）
# =========================
def get_stock(code):
    url = f"http://hq.sinajs.cn/list={code}"
    r = requests.get(url)
    data = r.text.split("=")[1].split(",")
    
    return {
        "code": code,
        "name": data[0],
        "price": float(data[3]),
        "open": float(data[1]),
        "high": float(data[4]),
        "low": float(data[5]),
        "vol": float(data[8])
    }

# 股票池（核心蓝筹）
stocks = [
    "sh600519", "sh600036", "sh601318",
    "sz000001", "sz000858", "sh601166",
    "sz300750", "sz002594"
]

data = []
for s in stocks:
    try:
        data.append(get_stock(s))
    except:
        continue

df = pd.DataFrame(data)

# =========================
# 多因子模型
# =========================
df["vol_score"] = df["vol"] / df["vol"].mean()
df["price_score"] = df["price"] / df["price"].mean()

df["score"] = df["vol_score"] * 0.6 + df["price_score"] * 0.4

df = df.sort_values("score", ascending=False)

# =========================
# 展示
# =========================
st.subheader("🔥 今日推荐")

for _, row in df.iterrows():
    st.markdown(f"""
### {row['code']} - {row['name']}
- 💰 现价：{row['price']}
- 📊 成交量：{row['vol']}
- ⭐ 评分：{row['score']:.2f}
""")

# =========================
# 热点提示
# =========================
st.subheader("🔥 市场状态")

avg = df["price"].pct_change().mean()

if avg > 0:
    st.success("市场偏多头：可做多")
else:
    st.warning("市场震荡/偏弱：控制仓位")
