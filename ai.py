# 予想の値を保存する
import csv
import pandas as pd
import numpy as np
from scipy import linalg
import urllib.request #ファイルダウンロード
import lhafile
import os
import datetime

def get_weight(filename, predict_rank):
    with open('train_csv_file/' + filename + '.csv') as f:
        reader = csv.reader(f)
        data = [row for row in reader]

    data = data[1:]
    data = np.array(data, dtype=float).T
    y = data[predict_rank]
    x = data[7:].T
    inv_x = np.linalg.pinv(x.T @ x)
    w = (inv_x @ x.T) @ y
    return w

def unzip(lzh_save_dir_path, txt_save_dir_path):
    files = os.listdir(lzh_save_dir_path)
    for filename in files:
        if filename.endswith(".lzh"):
            txt_file = lhafile.Lhafile(lzh_save_dir_path + filename)
            info = txt_file.infolist()
            name = info[0].filename
            open(txt_save_dir_path + name, "wb").write(txt_file.read(name))

def skip_line(skip_num, f):
    for _ in range(skip_num):
        skip = f.readline()
    return skip

def read_before_file(txt_save_dir_path, txt_file):
    f = open(txt_save_dir_path + txt_file, 'r', encoding='shift_jis')
    while True:
        line = f.readline()
        if "BGN" in line:
            race_info = f.readline()
            stadium_name = race_info[:9] #レース会場の名前
            skip_line(10, f)
            path = 'predict_csv_file/' + stadium_name + ".csv"
            with open(path, 'a') as csv_f:
                writer = csv.writer(csv_f)
                writer.writerows([["会場", race_info.replace("　", "")]])
                # print([["会場", race_info.replace("　", "")]])
                all_race_data = read_before_race_data(12, 6, f) #6選手×12レース分のデータを会場ごとに読み込む
                for i in range(len(all_race_data)):
                    writer.writerows([[str(i+1) + "R"]])
                    # print([[str(i+1) + "R"]])
                    for j in range(1):
                        w = get_weight(stadium_name, j+1)
                        # print(all_race_data[i])
                        predict = np.sum(w*all_race_data[i])
                        writer.writerows([["rank"+str(j+1), predict]])
                        # print([["rank"+str(j+1), predict]])
        if line == '':
            break
    f.close()

def read_before_race_data(race_num, player_num, f):
    all_race_data = []
    for i in range(race_num):
        stadium_data = f.readline().split() #レース会場のデータ

        type_name = ["一般", "予選", "選抜", "優勝", "特賞or特選", "その他"]
        type_membership = np.zeros(len(type_name))
        for j in range(len(type_name)):
            if j < 4:
                if type_name[j] in stadium_data[1]:
                    type_membership[j] = 1
            elif j == 4:
                if ('特賞' in stadium_data[1]) or ('特選' in stadium_data[1]):
                    type_membership[j] = 1
            elif j == 5 and np.sum(type_membership) == 0:
                type_membership[j] = 1

        # print("会場データ", stadium_data)

        skip_line(4, f) #不要な行を飛ばす
        arrange_stadium_data = [i+1]
        arrange_stadium_data = np.append(arrange_stadium_data, type_membership)
        # print(arrange_stadium_data)
        arrange_stadium_data = np.append(arrange_stadium_data, read_before_player_data(player_num, stadium_data, f))
        # print(arrange_stadium_data)
        all_race_data.append(list(arrange_stadium_data))
        # print(all_race_data)
    return all_race_data

def read_before_player_data(player_num, stadium_data, f):
    all_player_data = []
    for _ in range(player_num):
        player_data = f.readline()
        boat_num, toban, name, age, area, weight, rank, win_rate, win_rate2, stadium_win_rate, stadium_win_rate2, motor_no, motor_win_rate2, boat_no, boat_win_rate2, grades = player_data[0], player_data[2:6], player_data[6:10], player_data[10:12], player_data[12:14], player_data[14:16], player_data[16:18], player_data[18:23].replace(' ', ''), player_data[23:29].replace(' ', ''), player_data[29:34].replace(' ', ''), player_data[34:40].replace(' ', ''), player_data[40:43].replace(' ', ''), player_data[43:49].replace(' ', ''), player_data[49:52].replace(' ', ''), player_data[52:58].replace(' ', ''), player_data[58:-3].replace(' ', '')

        # print(boat_num, toban, name, age, area, weight, rank, win_rate, win_rate2, stadium_win_rate, stadium_win_rate2, motor_no, motor_win_rate2, boat_no, boat_win_rate2, grades)

# 所属支部を0,1で表現
        area_name = ["群馬", "埼玉", "東京", "静岡", "愛知", "三重", "福井", "滋賀", "大阪", "兵庫", "徳島", "香川", "岡山", "広島", "山口", "福岡", "佐賀", "長崎"]
        area_membership = np.zeros(len(area_name))
        area_membership[area_name.index(area)] = 1
        # area_membership = list(area_membership)
        # print(area_membership)

# 級別を0,1で表現
        rank_name = ["A1", "A2", "B1", "B2"]
        rank_membership = np.zeros(len(rank_name))
        rank_membership[rank_name.index(rank)] = 1
        # rank_membership = list(rank_membership)
        # print(rank_membership)

        arrange_player_data = [int(boat_num), int(toban), int(age), int(weight), float(win_rate), float(win_rate2), float(stadium_win_rate), float(stadium_win_rate2), int(motor_no), float(motor_win_rate2), int(boat_no), float(boat_win_rate2)]
        arrange_player_data = np.append(arrange_player_data, rank_membership)
        arrange_player_data = np.append(arrange_player_data, area_membership)
        arrange_player_data = list(arrange_player_data)
        # print(arrange_player_data)
        all_player_data =  np.append(all_player_data, arrange_player_data)

    skip_line(1, f)
    # print(all_player_data)
    return all_player_data

def download_before_file(yyyymmdd, save_dir_path):
    yyyymm = yyyymmdd[0:6]
    yymmdd = yyyymmdd[2:8]
    url = "http://www1.mbrace.or.jp/od2/B/" + yyyymm + "/b" + yymmdd + ".lzh"
    save_filename = os.path.basename(url)
    save_file_path = save_dir_path + save_filename
    try:
        with urllib.request.urlopen(url) as web_file, open(save_file_path, "wb") as local_file:
            local_file.write(web_file.read())
    except urllib.error.URLError as e:
        print(e)

column = ["R", "一般", "予選", "選抜", "優勝", "特賞or特選", "その他", "艇番", "登板", "年齢", "体重", "全国勝率", "全国2率", "当地勝率", "当地2率", "モーターNO", "モーター2率", "ボートNO", "ボート2率", "A1", "A2", "B1", "B2", "群馬", "埼玉", "東京", "静岡", "愛知", "三重", "福井", "滋賀", "大阪", "兵庫", "徳島", "香川", "岡山", "広島", "山口", "福岡", "佐賀", "長崎", "艇番", "登板", "年齢", "体重", "全国勝率", "全国2率", "当地勝率", "当地2率", "モーターNO", "モーター2率", "ボートNO", "ボート2率", "A1", "A2", "B1", "B2", "群馬", "埼玉", "東京", "静岡", "愛知", "三重", "福井", "滋賀", "大阪", "兵庫", "徳島", "香川", "岡山", "広島", "山口", "福岡", "佐賀", "長崎", "艇番", "登板", "年齢", "体重", "全国勝率", "全国2率", "当地勝率", "当地2率", "モーターNO", "モーター2率", "ボートNO", "ボート2率", "A1", "A2", "B1", "B2", "群馬", "埼玉", "東京", "静岡", "愛知", "三重", "福井", "滋賀", "大阪", "兵庫", "徳島", "香川", "岡山", "広島", "山口", "福岡", "佐賀", "長崎", "艇番", "登板", "年齢", "体重", "全国勝率", "全国2率", "当地勝率", "当地2率", "モーターNO", "モーター2率", "ボートNO", "ボート2率", "A1", "A2", "B1", "B2", "群馬", "埼玉", "東京", "静岡", "愛知", "三重", "福井", "滋賀", "大阪", "兵庫", "徳島", "香川", "岡山", "広島", "山口", "福岡", "佐賀", "長崎", "艇番", "登板", "年齢", "体重", "全国勝率", "全国2率", "当地勝率", "当地2率", "モーターNO", "モーター2率", "ボートNO", "ボート2率", "A1", "A2", "B1", "B2", "群馬", "埼玉", "東京", "静岡", "愛知", "三重", "福井", "滋賀", "大阪", "兵庫", "徳島", "香川", "岡山", "広島", "山口", "福岡", "佐賀", "長崎", "艇番", "登板", "年齢", "体重", "全国勝率", "全国2率", "当地勝率", "当地2率", "モーターNO", "モーター2率", "ボートNO", "ボート2率", "A1", "A2", "B1", "B2", "群馬", "埼玉", "東京", "静岡", "愛知", "三重", "福井", "滋賀", "大阪", "兵庫", "徳島", "香川", "岡山", "広島", "山口", "福岡", "佐賀", "長崎"]

before_lzh_save_dir_path = "./before_download/"
before_txt_save_dir_path = "./before_txtfile/"

train_days_start = datetime.date(2021, 5, 8)
train_days_end = datetime.date(2021, 5, 8)
train_days = (train_days_start - train_days_end).days + 1

# train_days_startから始まって、(train_days)日分の結果ファイルを読み込みcsvファイル化
for i in range(train_days):
    day = train_days_start.strftime("%Y%m%d")
    train_days_start = train_days_start - datetime.timedelta(days=1)
    # download_before_file(day, before_lzh_save_dir_path)
    # unzip(before_lzh_save_dir_path, before_txt_save_dir_path)
    read_before_file(before_txt_save_dir_path, "B" + day[2:] + ".TXT")