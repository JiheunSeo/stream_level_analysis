import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def level_plot(level_datas):
    plt.figure(figsize=(20, 6))
    for level_data in level_datas:
        # 시간을 기준으로 데이터 정렬
        level_data.sort_values(by='local_time', inplace=True)
        
        # 각 데이터를 시간 순서로 그래프에 추가
        plt.plot(level_data['local_time'], level_data['sample_value'], marker='o', linestyle='-', label=level_data['local_day'].iloc[0], markersize=2)

    plt.xlabel('Time of Day (Hour:Minute)')
    plt.ylabel('Sample Value')
    plt.title('Hourly Level Data Across Multiple Dates')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid(True)

    # x축 눈금 설정: 10분 간격으로 설정
    plt.xticks([time for time in level_data['local_time'] if time.endswith(':08')])

    plt.tight_layout()
    plt.show()

def data_load(data_dir):
    file_paths =  [os.path.join(data_dir, file) for file in os.listdir(data_dir) if file.endswith('.csv')]

    level_datas = []
    for file_path in file_paths:
        level_data = pd.read_csv(file_path, encoding='utf-8')
        level_data = level_data[['Site Name', 'Local(yyyy/MM/dd HH:mm:ss)', 'Sample Value']]
        level_data.columns = ['site_name', 'local_time', 'sample_value']
        
        # local_time을 날짜(local_day)와 시간(local_time)으로 나누기
        level_data['local_day'] = pd.to_datetime(level_data['local_time']).dt.date
        level_data['hour'] = pd.to_datetime(level_data['local_time']).dt.hour
        level_data['minute'] = pd.to_datetime(level_data['local_time']).dt.minute
        level_data['hour_minute'] = level_data['hour'].map('{:02}'.format) + ':' + level_data['minute'].map('{:02}'.format)
        level_data['local_time'] = pd.to_datetime(level_data['local_time']).dt.strftime('%H:%M')
        level_datas.append(level_data)
    
    return level_datas

def statistics_per_day(level_datas):
    for level_data in level_datas:
        # 시간별 통계치 계산
        grouped = level_data.groupby('hour_minute')['sample_value'].agg(['min', 'max', 'mean', 'median'])
        print(f"Statistics for {level_data['local_day'].iloc[0]}:")
        print(grouped)
        file_name = f"./result/statistics_per_day_{level_data['local_day'].iloc[0]}.csv"
        grouped.to_csv(file_name, index=False)
        print()

def statistics_all_data_per_hour(level_datas):
  grouped_stats = all_data.groupby('hour_minute')['sample_value'].agg(['min', 'max', 'mean', 'median'])
  print("Hourly Statistics Across All Dates:")
  print(grouped_stats)
  grouped_stats.to_csv('./result/statistics_all_day.csv',index=True)

def boxplot_all_data_per_hour(all_data):
  plt.figure(figsize=(12, 8))
  all_data.boxplot(column='sample_value', by='hour_minute', grid=True)
  plt.xlabel('Hour of Day')
  plt.ylabel('Sample Value')
  plt.title('Box Plot of Sample Value by Hour of Day')
  plt.suptitle('')
  plt.show()

def concat_level_data(level_datas):
  return pd.concat(level_datas, ignore_index=True)

def find_outliers(all_data):
  grouped_stats = all_data.groupby('hour_minute')['sample_value'].describe()
  grouped_stats['IQR'] = grouped_stats['75%'] - grouped_stats['25%']
  grouped_stats['lower_bound'] = grouped_stats['25%'] - 1.5 * grouped_stats['IQR']
  grouped_stats['upper_bound'] = grouped_stats['75%'] + 1.5 * grouped_stats['IQR']
  grouped_stats.to_csv('./result/range_of_outliers.csv',index=True)

  # 이상치 찾기
  outliers = pd.DataFrame()
  for hour_minute, data in all_data.groupby('hour_minute'):
    lower_bound = grouped_stats.loc[hour_minute, 'lower_bound']
    upper_bound = grouped_stats.loc[hour_minute, 'upper_bound']
        
    hour_outliers = data[(data['sample_value'] < lower_bound) | (data['sample_value'] > upper_bound)]
    hour_outliers.loc[:, 'hour_minute'] = hour_minute
    outliers = pd.concat([outliers, hour_outliers])
    outliers.to_csv('./result/outliers.csv',index=False)
  return outliers

# 데이터 로드
data_dir = './data/'
level_datas = data_load(data_dir)

# 그래프 그리기
level_plot(level_datas)

# 모든 일자 별 데이터
all_data = concat_level_data(level_datas)

# 통계치 출력
statistics_per_day(level_datas)
statistics_all_data_per_hour(all_data)
boxplot_all_data_per_hour(all_data)

#이상치 찾기
outliers = find_outliers(all_data)
print("Outliers")
print(outliers)


