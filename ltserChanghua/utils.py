import pandas as pd
data = pd.read_csv("./post/InterviewContent.csv", index_col=False)
data['interview_date'] = pd.to_datetime(data['interview_date']).dt.strftime("%Y-%m-%d")
data.to_csv('interview_content_post_process.csv', index=False, encoding='utf-8')