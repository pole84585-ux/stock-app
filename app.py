import tushare as ts
import pandas as pd
import streamlit as st
from datetime import datetime

st.title("📊 A股量化选股系统")

TOKEN = st.text_input("请输入Tushare Token", type="password")

if TOKEN:
    ts.set_token(TOKEN)
    pro = ts.pro_api()

    START_DATE = "20230101"
    END_DATE = datetime.today().strftime("%Y%m%d")

    import pandas as pd
stocks = pd.read_csv("data.csv")

def get_data(ts_code):
        df = pro.daily(ts_code=ts_code, start_date=START_DATE, end_date=END_DATE)
        df = df.sort_values("trade_date")

        df['MA20'] = df['close'].rolling(20).mean()
        df['MA60'] = df['close'].rolling(60).mean()
        df['VOL5'] = df['vol'].rolling(5).mean()
        df['HIGH20'] = df['high'].rolling(20).max()

        return df

    def score_stock(df):
        if len(df) < 60:
            return 0

        latest = df.iloc[-1]
        score = 0

        if latest['MA20'] > latest['MA60']:
            score += 30
        if latest['close'] >= latest['HIGH20']:
            score += 40
        if latest['vol'] > 1.5 * latest['VOL5']:
            score += 30

        return score

    if st.button("🚀 开始选股"):

        results = []

        for i, row in stocks.head(50).iterrows():
            try:
                df = get_data(row['ts_code'])
                score = score_stock(df)
                import time
                time.sleep(0.5)

                if score > 60:
                    results.append({
                        "name": row['name'],
                        "industry": row['industry'],
                        "score": score
                    })
            except:
                continue

        if results:
            df_res = pd.DataFrame(results).sort_values(by="score", ascending=False).head(5)

            st.subheader("📈 推荐股票")

            for i, row in df_res.iterrows():
                stars = "⭐" * (row['score'] // 20)

                st.write(f"{row['name']}（{row['industry']}） {stars}")
                st.write("👉 买点：突破新高 + 放量")
                st.write("👉 止损：-5%")
                st.write("👉 止盈：+15% / +20%")

            st.subheader("🔥 热点板块")
            hot = df_res['industry'].value_counts().head(3)

            for ind in hot.index:
                st.write(ind)
        else:
            st.warning("今日无信号")
