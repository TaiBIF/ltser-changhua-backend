import pandas as pd
data = pd.read_excel('InterviewContent.xlsx')
data['interview_date'] = pd.to_datetime(data['interview_date'], format='%Y-%m-%d')
data['interview_date'] = data['interview_date'].dt.strftime('%Y-%m-%d')
data.to_csv("InterviewContent_postprocess.csv", index=False, encoding='utf-8')