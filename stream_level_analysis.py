import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def level_plot(level_data):
    # 'hour_minute'를 datetime 형식으로 변환
    level_data['hour_minute'] = pd.to_datetime(level_data['hour_minute'], format='%H:%M')
    
    level_data_per_day = []
    unique_dates = level_data['local_day'].unique()
    for date in unique_dates:
        # 각 날짜별 데이터 추출
        date_data = level_data[level_data['local_day'] == date].copy()
        # 리스트에 추가
        level_data_per_day.append(date_data)

    plt.figure(figsize=(30, 15))

    for date_data in level_data_per_day:
        # 시간을 기준으로 데이터 정렬
        date_data.sort_values(by='hour_minute', inplace=True)
        
        # 각 데이터를 시간 순서로 그래프에 추가
        plt.plot(date_data['hour_minute'], date_data['sample_value'], marker='o', linestyle='-', label=date_data['local_day'].iloc[0], markersize=2)

    plt.xlabel('Time of Day (Hour:Minute)')
    plt.ylabel('Sample Value')
    plt.title('Hourly Level Data Across Multiple Dates')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.grid(True)

    # x축 눈금 설정: 10분 간격으로 설정
    plt.xticks(level_data['hour_minute'][::10], rotation=45)
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))

    plt.tight_layout()
    plt.show()



def data_load(data_dir):
    file_paths =  [os.path.join(data_dir, file) for file in os.listdir(data_dir) if file.endswith('.csv')]

    level_datas = []
    for file_path in file_paths:
        level_data = pd.read_csv(file_path, encoding='utf-8')
        level_data = level_data[['Site Name', 'Local(yyyy/MM/dd HH:mm:ss)', 'Sample Value']]
        level_data.columns = ['site_name', 'local_time', 'sample_value']
        
        level_data['local_day'] = pd.to_datetime(level_data['local_time']).dt.date
        level_data['hour'] = pd.to_datetime(level_data['local_time']).dt.hour
        level_data['minute'] = pd.to_datetime(level_data['local_time']).dt.minute
        level_data['hour_minute'] = level_data['hour'].map('{:02}'.format) + ':' + level_data['minute'].map('{:02}'.format)
        level_data['local_time'] = pd.to_datetime(level_data['local_time']).dt.strftime('%H:%M')
        level_datas.append(level_data)
    
    return pd.concat(level_datas, ignore_index=True)

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
  grouped_stats = level_datas.groupby('hour_minute')['sample_value'].agg(['min', 'max', 'mean', 'median'])
  print("Statistics Across All Dates:")
  print(grouped_stats)
  grouped_stats.to_csv('./result/statistics_all_day.csv',index=True)

def boxplot_all_data_per_hour(level_datas):
    plt.figure(figsize=(19, 8))
    
    # Boxplot 그리기
    boxplot = level_datas.boxplot(column='sample_value', by='hour_minute', grid=True)
    
    # x축 라벨을 모든 hour_minute 값으로 설정
    boxplot.set_xticklabels(level_datas['hour_minute'].unique(), rotation=90)
    
    # 모든 x축 라벨을 가져옴
    x_labels = boxplot.get_xticklabels()
    
    # x축 라벨 중 :08로 끝나는 것만 표시하도록 설정
    new_labels = [label.get_text() if label.get_text().endswith(':08') else '' for label in x_labels]
    boxplot.set_xticklabels(new_labels)
    
    plt.xlabel('h/m of Day')
    plt.ylabel('Sample Value')
    plt.title('Box Plot of Sample Value by h/m of Day')
    plt.suptitle('')
    plt.show()
def concat_level_data(level_datas):
  return pd.concat(level_datas, ignore_index=True)

def find_outliers(level_datas):
  grouped_stats = level_datas.groupby('hour_minute')['sample_value'].describe()
  grouped_stats['IQR'] = grouped_stats['75%'] - grouped_stats['25%']
  grouped_stats['lower_bound'] = grouped_stats['25%'] - 1.5 * grouped_stats['IQR']
  grouped_stats['upper_bound'] = grouped_stats['75%'] + 1.5 * grouped_stats['IQR']
  grouped_stats.to_csv('./result/range_of_outliers.csv',index=True)

  # 이상치 찾기
  outliers = pd.DataFrame()
  for hour_minute, data in level_datas.groupby('hour_minute'):
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

# 통계치 출력
# statistics_per_day(level_datas)
statistics_all_data_per_hour(level_datas)
boxplot_all_data_per_hour(level_datas)

#이상치 찾기
outliers = find_outliers(level_datas)
print("Outliers")
print(outliers)


