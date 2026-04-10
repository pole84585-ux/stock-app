import tushare as ts
import pandas as pd

ts.set_token("你的token")
pro = ts.pro_api()

stocks = pro.stock_basic(fields="ts_code,name,industry")

data = []

for code in stocks['ts_code'][:300]:
    try:
        df = pro.daily(ts_code=code)
        df = df.sort_values("trade_date")

        latest = df.iloc[-1]

        data.append([
            code,
            latest['close'],
            latest['vol'],
            latest['pct_chg']
        ])

    except:
        continue

pd.DataFrame(data, columns=["code","close","vol","pct"]).to_csv("data.csv", index=False)

print("更新完成")
