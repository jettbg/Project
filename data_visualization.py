import pandas as pd
import mplfinance as mpf

# 从CSV加载数据
df = pd.read_csv('600519.csv', parse_dates=['date'])
df.set_index('date', inplace=True)  # 设置日期为索引

# 计算移动平均线（MA5和MA20）
df['MA5'] = df['Close'].rolling(window=5).mean()
df['MA20'] = df['Close'].rolling(window=20).mean()

# 绘制K线图 + 成交量 + 移动平均线
mpf.plot(df, 
         type='candle', 
         volume=True, 
         style='charles',
         title='中芯国际K线图',
         ylabel='价格 (元)',
         ylabel_lower='成交量',
         mav=(5, 20),  # 添加MA5和MA20
         savefig='kline.png')  # 保存为图片
