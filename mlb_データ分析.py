# -*- coding: utf-8 -*-
"""mlb_データ分析.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1clkwHekVzsR3MJz01dxoKwTmE6jrmTeJ
"""

!pip install pandas html5lib beautifulsoup4 numpy scikit-learn matplotlib seaborn tqdm
import pandas as pd
import numpy as np
from tqdm.notebook import tqdm
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import statsmodels.api as sm

url = 'https://www.baseball-reference.com/leagues/majors/2022-standard-batting.shtml#teams_standard_batting'
result = pd.read_html(url)  # データの読み込み
print(len(result))  # 読み込みこまれたデータの数
df = result[0]  # 結果に含まれるデータを取り出す
df   # データの表示

# year　のデータを読み込む
def download_stat(year):
    url = f'https://www.baseball-reference.com/leagues/majors/{year}-standard-batting.shtml#teams_standard_batting'
    result = pd.read_html(url)

    return result[0]

# start_year から end_year までのデータを取得し、各年で CSV を保存する
def main():
    start_year = 2013
    end_year = 2023
    data_dir = '/content'

    for year in tqdm(range(start_year, end_year+1)):
        stat = download_stat(year)
        name = f'leagues-standard-batting-{year}.csv'
        stat.to_csv(os.path.join(data_dir, name), index=None)

main()

def read_stat(year, data_dir):
    name = f'leagues-standard-batting-{year}.csv'
    stat = pd.read_csv(os.path.join(data_dir, name))
    return stat

read_stat(2023, '/content')

# 指定した年の範囲のデータを読み込み、1つのDataFrameにまとめる
def read_stat_all(start_year, end_year, data_dir):
    list_stat = []

    for year in tqdm(range(start_year, end_year+1)):
        stat = read_stat(year, data_dir)
        stat['year'] = year
        list_stat.append(stat)

    return pd.concat(list_stat)

start_year = 2013
end_year = 2023
data_dir = '/content'

stat_all = read_stat_all(start_year, end_year, data_dir)    # 全データを読み込む
stat_all['Tm'].value_counts()

def reshape_team_name(stat_all):
    dict_team_name_replace = {
        'Cleveland Indians':'Cleveland Guardians',
        'Florida Marlins': 'Miami Marlins',
        'Los Angeles Angels of Anaheim': 'Los Angeles Angels',
    }

    list_team_name_delete = [np.nan, 'Tm', 'League Average']

    stat_all = stat_all[~stat_all['Tm'].isin(list_team_name_delete)]    # 行の削除
    stat_all = stat_all.replace({'Tm': dict_team_name_replace})     # チーム名を統一

    return stat_all

stat_all = reshape_team_name(stat_all)
print(stat_all['Tm'].value_counts())

#objectからfloat
for target in stat_all.columns[1:29].values:
  stat_all[target] = pd.to_numeric(stat_all[target])

pd.set_option('display.max_columns', None)
stat_all

def main(data, target):
    fig, ax = plt.subplots(figsize=(6, 6))
    sns.scatterplot(data=data, x=target, y='R/G', hue='year',
                     ax=ax,palette='deep')

    plt.show()

main(stat_all, 'BA')

main(stat_all, 'BA')

df = stat_all.drop(['Tm','G','R','#Bat','BatAge','OBP','SLG'],axis=1)
df

df.corr().style.background_gradient(axis=None)

df1 = df.drop(['AB','H','2B','3B','RBI','BB','TB','HR','PA','LOB','year','OPS','OPS+'],axis=1)
df1.corr().style.background_gradient(axis=None)

df_X = df.drop('R/G', axis=1)
df_y = df['R/G']

df_X = sm.add_constant(df_X)

model = sm.OLS(df_y, df_X)
result = model.fit()
print(result.summary())

df_X = df1.drop('R/G', axis=1)
df_y = df1['R/G']

df_X = sm.add_constant(df_X)

model = sm.OLS(df_y, df_X)
result = model.fit()
print(result.summary())

# 回帰モデルを計算する
def build_model(x, y):
    model = LinearRegression()
    model.fit(x, y)

    return model

# 回帰直線の式、決定係数を整形して表示する
def print_summary(model, x, y):
    print(f'y= {model.coef_[0][0]:.3f}*x + {model.intercept_[0]:.3f}')
    print('score： ', model.score(x, y))

def main(data, target,target2):
    # DataFrameから説明変数targetと得点を抽出する
    x = data[[target]]
    y = data[[target2]]

    # 回帰分析
    model = build_model(x, y)
    print_summary(model, x, y)

    pred = model.predict(x)
    # プロット
    fig, ax = plt.subplots(figsize=(6, 6))
    # 散布図
    sns.scatterplot(data=data, x=target, y=target2, hue='year',
                    ax=ax, palette='deep')
    # 回帰直線
    sns.lineplot(
        data={'x':x.values.reshape(-1), 'y':pred.reshape(-1)},
        x='x', y='y'
    )
    plt.show()

main(stat_all, 'OPS','R/G')

main(stat_all, 'BA','R/G')