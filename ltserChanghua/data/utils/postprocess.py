
import pandas as pd
# 读取 CSV 文件
df = pd.read_csv('news.csv')
df['date'] = pd.to_datetime(df['date'], format='%Y/%m/%d')

df['date'] = df['date'].dt.strftime('%Y-%m-%d')
df.to_csv('news_processed.csv', index=False)
