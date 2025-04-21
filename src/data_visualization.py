import os
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def plot_kline(data: pd.DataFrame, title: str = 'K线图', save_path: str = 'kline.png') -> None:
    """绘制K线图并保存为图片"""
    try:
        logger.info(f"数据列名: {data.columns}")
        logger.info(f"数据预览:\n{data.head()}")

        if 'date' not in data.columns:
            raise ValueError("数据缺少 'date' 列")

        # 转换日期格式并去除无效数据
        data['date'] = pd.to_datetime(data['date'], errors='coerce')
        data = data.dropna(subset=['date'])

        # 临时设置索引（仅用于绘图）
        df_plot = data.copy()
        df_plot.set_index('date', inplace=True)

        mpf.plot(df_plot,
                 type='candle',
                 volume=True,
                 style='charles',
                 title=title,
                 ylabel='Price',
                 ylabel_lower='Volume',
                 mav=(5, 20),
                 savefig=save_path)

        logger.info(f"{title} 绘制完成，已保存至 {save_path}")
    except Exception as e:
        logger.error(f"绘制K线图失败: {str(e)}")

def load_data(file_path: str) -> pd.DataFrame:
    """从CSV文件加载数据,保持 'date' 为列"""
    if not os.path.exists(file_path):
        logger.error(f"文件 {file_path} 不存在")
        return pd.DataFrame()

    try:
        df = pd.read_csv(file_path, parse_dates=['date'])

        if 'date' not in df.columns or 'Close' not in df.columns:
            logger.error("数据文件中缺少必要的列")
            return pd.DataFrame()

        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])

        # 不再设置索引，保持 date 为列
        return df
    except Exception as e:
        logger.error(f"加载数据失败: {str(e)}")
        return pd.DataFrame()

def calculate_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    """计算 MA5 和 MA20"""
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    return df

# 主函数入口
if __name__ == "__main__":
    stock_codes = ['000001.SZ', '01810.HK']
    start = '20250101'
    end = '20250410'

    for code in stock_codes:
        try:
            input_path = f"{code.replace('.', '_')}_adjusted.csv"
            df = load_data(input_path)
            if df.empty:
                logger.error(f"{input_path} 数据加载失败")
                continue

            df = calculate_moving_averages(df)

            title = f'{code} '
            save_path = f"{code.replace('.', '_')}_kline.png"
            plot_kline(df, title=title, save_path=save_path)

            print(f"{code} 获取数据量：{len(df)}条")
            print(f"日期范围：{df['date'].min()} 至 {df['date'].max()}")
        except Exception as e:
            logger.error(f"{code} 绘制失败: {str(e)}")



