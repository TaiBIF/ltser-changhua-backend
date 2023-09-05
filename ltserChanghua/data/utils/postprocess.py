
import pandas as pd
# 读取 CSV 文件
df = pd.read_csv('news.csv')

#df.insert(len(df.columns), 'views', 0)
# id_values = range(708, 708 + len(df))
# df.insert(0, 'id', id_values)
df['date'] = pd.to_datetime(df['date'], format='%Y/%m/%d')
# #
df['date'] = df['date'].dt.strftime('%Y-%m-%d')
df.to_csv('news_post.csv', encoding='utf-8', index=False)
