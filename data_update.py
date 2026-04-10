import akshare as ak
import pandas as pd

stocks = ["600519", "600036", "601318", "000001", "000858", "300750"]

all_data = []

for s in stocks:
    try:
        df = ak.stock_zh_a_hist(symbol=s, period="daily", adjust="qfq")
        df = df.tail(200)

        df["ret"] = df["收盘"].pct_change()
        df["vol"] = df["成交量"]
        df["vol_chg"] = df["vol"].pct_change()
        df["code"] = s

        all_data.append(df)

    except:
        continue

# =========================
# 北向资金历史（新增🔥）
# =========================
try:
    north = ak.stock_hsgt_north_net_flow_in_em()
    north = north.tail(5)
    north.to_csv("north.csv", index=False)
except:
    pass

# =========================
# 保存股票数据
# =========================
final_df = pd.concat(all_data)
final_df.to_csv("data.csv", index=False)

print("✅ 数据更新完成")
