import tushare as ts   #tushare：获取股票数据
import pandas as pd    # Pandas用于数据处理和分析 
import time

# 设置Tushare Token
ts.set_token('')
pro = ts.pro_api()

def fetch_stock_data(ts_code, start_date, end_date):
    """
    获取股票历史数据
    param ts_code: 股票代码（如 '600519.SH'）
    param start_date: 开始日期（格式 如'20250311'）
    param end_date: 结束日期
    return: DataFrame
    """
    try:
        #使程序暂停 1 秒钟，避免短时间内过多 API 请求而被限流
        time.sleep(1)
        #通过 pro.daily() 方法从 Tushare 获取该股票在指定日期范围内的 日线交易数据
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        if df.empty:
            print("未获取到数据，请检查基金代码或权限")
            return None
        df = df.sort_values('trade_date')  # 按日期升序排序
        df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')  # 转换日期格式
        df.rename(columns={
            'trade_date': 'date',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'vol': 'Volume'
        }, inplace=True)
        return df[['date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    except Exception as e:
        print(f"数据获取失败: {e}")
        return None

# 获取2024年数据
df = fetch_stock_data('688981.SH', '20250101', '20250228')
if df is not None:
    df.to_csv('600519.csv', index=False)  # 保存到CSV
    print("数据已保存至600519.csv")
else:
     print("数据获取失败")  

