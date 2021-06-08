import csv
import pandas as pd
import numpy as np
from scipy import linalg
import urllib.request #ファイルダウンロード
import lhafile
import os
import datetime
import csv

race = "ボートレース　津　"
filename = "train_csv_file/" + race + ".csv"

with open(filename) as f:
    reader = csv.reader(f)
    data = [row for row in reader]

train_num = 2400
predict_rank = 1

data = data[1:]
print("データ数", len(data))
print("学習数", train_num)
print("テスト数", len(data) - train_num)
train_data = data[:train_num]
test_data = data[train_num:]

train_data = np.array(train_data, dtype=float).T
test_data = np.array(test_data, dtype=float).T

train_y = train_data[predict_rank]
test_y = test_data[predict_rank]

train_x = train_data[7:].T
test_x = test_data[7:].T

inv_x = np.linalg.pinv(train_x.T @ train_x)
w = (inv_x @ train_x.T) @ train_y
predict_y = test_x @ w
gosa = (predict_y - test_y)*(predict_y - test_y)
# print(predict_y)
print("予測値との誤差", np.sum(gosa)/len(predict_y))

trained = train_x @ w
gosa = (trained - train_y)*(trained - train_y)
# print(trained)
print("学習値との誤差", np.sum(gosa)/len(train_y))
