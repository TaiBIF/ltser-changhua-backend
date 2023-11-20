import pandas as pd
import requests
from datetime import datetime
from tqdm import tqdm

url = "https://data.moenv.gov.tw/api/v2/aqx_p_143"
params = {
    'api_key': '5b537c83-6b6a-4802-bcdf-279368ad172e',
    'filters': 'SiteName,EQ,二林|itemengname,EQ,AMB_TEMP,CH4,CO,NMHC,NO,NO2,NOx,O3,PM2.5,RAINFALL,RH,SO2,THC,WD_HR,'
               'WIND_DIREC,'
               'WIND_SPEED,WS_HR',
    'limit': '1000',
    'offset': '0'
}

data_list = []
stop_date = datetime(2023, 1, 1, 0, 0)  # set the stop date to 2023-01-01 00:00:00

with tqdm(desc='Fetching Data') as pbar:
    while True:  # Run until break condition is met
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()

            records = data.get('records', [])
            for record in records:
                monitordate = record.get('monitordate', '')
                itemengname = record.get('itemengname', '')
                concentration = record.get('concentration', '')
                date_obj = datetime.strptime(monitordate, '%Y-%m-%d %H:%M')

                # Check if the date is earlier than the stop_date, then break the loop
                if date_obj < stop_date:
                    break

                date_str = date_obj.strftime('%Y/%m/%d')
                hour = date_obj.hour
                data_list.append(
                    {'測站': '大城', '日期': date_str, '測項': itemengname, 'hour': hour,
                     'concentration': concentration})

            else:  # This will only run if the for loop didn't hit a 'break', meaning we need to fetch the next page
                pbar.update(1)
                params['offset'] = str(int(params['offset']) + int(params['limit']))
                continue

            break  # This will run if we hit a 'break' in the for loop, meaning we reached the stop_date

        else:
            print(f"Failed to retrieve data. Status Code: {response.status_code}")
            break

df = pd.DataFrame(data_list)
df_pivot = df.pivot_table(index=['測站', '日期', '測項'], columns='hour', values='concentration',
                          aggfunc='first').reset_index()
df_pivot.columns.name = None

df_pivot.columns = [str(col) if isinstance(col, int) else col for col in df_pivot.columns]
cols = [col for col in df_pivot.columns if col not in ['測站', '日期', '測項']]
df_pivot[cols] = df_pivot[cols].apply(pd.to_numeric, errors='coerce')
df_pivot.columns = [int(col) if col.isdigit() else col for col in df_pivot.columns]
df_pivot.sort_values(by=['日期', '測項'], inplace=True)
df_pivot.to_excel('output.xlsx', index=False, engine='openpyxl')
