import os
import tushare as ts
import pandas as pd
import re
from dotenv import load_dotenv
from typing import Optional, Union
from datetime import datetime
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetchError(Exception):
    """自定义数据获取异常"""
    pass

# 从环境变量读取 Tushare Token
load_dotenv()  # 加载 .env 中的环境变量
token = os.getenv("TUSHARE_TOKEN")
if not token:
    raise ValueError("请设置环境变量 TUSHARE_TOKEN")

ts.set_token(token)
pro = ts.pro_api()

def identify_market(ts_code: str) -> str:
    """判断股票市场类型:A股、港股"""
    if re.match(r'^\d{6}\.(SH|SZ)$', ts_code):
        return 'A'
    elif re.match(r'^\d{5,6}\.HK$', ts_code):  
        return 'HK'
    else:
        raise ValueError("股票代码格式不正确")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_stock_data(
    ts_code: str,
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    adj: str = 'qfq'  # 'qfq'表示前复权, 'hfq'表示后复权, None表示不复权
) -> Optional[pd.DataFrame]:
    """自动识别市场并获取对应股票的日线数据，支持复权处理"""
    try:
        market = identify_market(ts_code)
        start = pd.to_datetime(start_date).strftime('%Y%m%d')
        end = pd.to_datetime(end_date).strftime('%Y%m%d')

        # 获取数据
        if market == 'A':
            df = pro.daily(ts_code=ts_code, start_date=start, end_date=end, adj=adj)  # 这里加了复权参数
        elif market == 'HK':
            df = pro.hk_daily(ts_code=ts_code, start_date=start, end_date=end)
        else:
            raise DataFetchError("无法识别市场类型")

        if df.empty:
            logger.warning(f"未找到{ts_code}在{start}-{end}期间的数据")
            return None

        # 字段映射（字段统一）
        column_mapping = {
            'trade_date': 'date',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'vol': 'Volume'
        }
        df = df.rename(columns=column_mapping)

        # 时间格式标准化
        df = (
            df.assign(date=lambda x: pd.to_datetime(x['date']))
              [['date', 'Open', 'High', 'Low', 'Close', 'Volume']]
              .sort_values('date')
              .reset_index(drop=True)
        )

        if df['date'].duplicated().any():
            logger.warning("存在重复日期数据，正在去重...")
            df = df.drop_duplicates('date', keep='last')

        return df

    except Exception as e:
        logger.error(f"数据获取失败: {str(e)}")
        raise DataFetchError("Tushare请求失败") from e

if __name__ == "__main__":
    stock_codes = ['000001.SZ', '01810.HK']
    start = '20250101'
    end = '20250410'

    for code in stock_codes:
        try:
            df = fetch_stock_data(code, start, end, adj='qfq')  # 使用前复权
            if df is not None:
                output_path = f"{code.replace('.', '_')}_adjusted.csv"
                df.to_csv(output_path, index=False)
                logger.info(f"{code} 数据已保存至 {output_path}")
                print(f"{code} 获取数据量：{len(df)}条")
                print(f"日期范围：{df['date'].min()} 至 {df['date'].max()}")
        except DataFetchError:
            logger.error(f"{code} 数据获取失败")



