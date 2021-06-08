# 2020/4/2までは学習済み
# train_csv_fileに保存する
#出走表をレースごとに分けて数値化し、説明変数と目的変数として保存する。学習データを作るプログラム。
import urllib.request #ファイルダウンロード
import lhafile
import os
import numpy as np
import csv
import datetime
from tqdm import tqdm

def skip_line(skip_num, f):
    for _ in range(skip_num):
        skip = f.readline()
    return skip

def skip_line_to_word(f, word):
    while True:
        line = f.readline()
        if word in line:
            break
    return line

def skip_to_race_data(f):
    while True:
        line = f.readline()
        if "Ｒ" in line and "ｍ" in line:
            break
    return line

def count_cancel_race(f):
    cancel_race = np.zeros(12)
    race_num = 1
    while race_num <= 12:
        line = f.readline()
        if str(race_num) in line: #第何Rか書いてある行に処理をする(同着の場合、書いていない行があるので)
            if "中" in line: #中止になったか否か
                cancel_race[race_num-1] = 1
            race_num += 1
    return cancel_race

def read_before_file(txt_file, column):
    f = open("before_txtfile/B" + txt_file, 'r', encoding='shift_jis')
    f_result = open("result_txtfile/K" + txt_file, 'r', encoding='shift_jis')
    while True:
        line = f.readline()
        skip_line(1, f_result)
        if "BGN" in line:
            stadium_name = f.readline()[:9] #レース会場の名前
            if "この場のデータ更新は、いましばらくお待ちください。" in skip_line(3, f):
                skip_line_to_word(f, "END")
                skip_line_to_word(f_result, "END")
                continue
            skip_line_to_word(f_result, "払戻金")
            cancel_race = count_cancel_race(f_result)

            if np.sum(cancel_race) == 12:
                skip_line_to_word(f, "END")
                skip_line_to_word(f_result, "END")
                continue

            all_race_data = []
            for i in range(12):
                if cancel_race[i] == 0:
                    race_data = skip_to_race_data(f)
                    skip_line_to_word(f_result, "---")
                    ranking = []
                    for j in range(6):
                        player = f_result.readline()
                        ranking.append(player[6])
                    judge = skip_line(2, f_result)
                    if "レース不成立" in judge:
                        continue

                    type_name = ["一般", "予選", "選抜", "優勝", "特賞or特選", "その他"]
                    type_membership = np.zeros(len(type_name))
                    for j in range(len(type_name)):
                        if j < 4:
                            if type_name[j] in race_data[1]:
                                type_membership[j] = 1
                        elif j == 4:
                            if ('特賞' in race_data[1]) or ('特選' in race_data[1]):
                                type_membership[j] = 1
                        elif j == 5 and np.sum(type_membership) == 0:
                            type_membership[j] = 1

                    skip_line_to_word(f, "---")
                    skip_line_to_word(f, "---")
                    arranged_race_data = [txt_file[:-4]]
                    arranged_race_data = np.append(arranged_race_data, ranking)
                    arranged_race_data = np.append(arranged_race_data, i+1)
                    arranged_race_data = np.append(arranged_race_data, type_membership)
                    arranged_race_data = np.append(arranged_race_data, read_before_player_data(6, f))
                    all_race_data.append(list(arranged_race_data))
                else:
                    skip_line(12, f)

            path = 'train_csv_file/' + stadium_name + ".csv"
            with open(path, 'a') as csv_f:
                writer = csv.writer(csv_f)
                if os.path.getsize(path) == 0:
                    writer.writerow(column)
                writer.writerows(all_race_data)
        if line == '':
            break
    f.close()

def read_before_player_data(player_num, f):
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
        all_player_data =  np.append(all_player_data, arrange_player_data)

    return all_player_data

column = ["日付", "１位", "２位", "３位", "４位", "５位", "６位", "R", "一般", "予選", "選抜", "優勝", "特賞or特選", "その他", "艇番", "登板", "年齢", "体重", "全国勝率", "全国2率", "当地勝率", "当地2率", "モーターNO", "モーター2率", "ボートNO", "ボート2率", "A1", "A2", "B1", "B2", "群馬", "埼玉", "東京", "静岡", "愛知", "三重", "福井", "滋賀", "大阪", "兵庫", "徳島", "香川", "岡山", "広島", "山口", "福岡", "佐賀", "長崎", "艇番", "登板", "年齢", "体重", "全国勝率", "全国2率", "当地勝率", "当地2率", "モーターNO", "モーター2率", "ボートNO", "ボート2率", "A1", "A2", "B1", "B2", "群馬", "埼玉", "東京", "静岡", "愛知", "三重", "福井", "滋賀", "大阪", "兵庫", "徳島", "香川", "岡山", "広島", "山口", "福岡", "佐賀", "長崎", "艇番", "登板", "年齢", "体重", "全国勝率", "全国2率", "当地勝率", "当地2率", "モーターNO", "モーター2率", "ボートNO", "ボート2率", "A1", "A2", "B1", "B2", "群馬", "埼玉", "東京", "静岡", "愛知", "三重", "福井", "滋賀", "大阪", "兵庫", "徳島", "香川", "岡山", "広島", "山口", "福岡", "佐賀", "長崎", "艇番", "登板", "年齢", "体重", "全国勝率", "全国2率", "当地勝率", "当地2率", "モーターNO", "モーター2率", "ボートNO", "ボート2率", "A1", "A2", "B1", "B2", "群馬", "埼玉", "東京", "静岡", "愛知", "三重", "福井", "滋賀", "大阪", "兵庫", "徳島", "香川", "岡山", "広島", "山口", "福岡", "佐賀", "長崎", "艇番", "登板", "年齢", "体重", "全国勝率", "全国2率", "当地勝率", "当地2率", "モーターNO", "モーター2率", "ボートNO", "ボート2率", "A1", "A2", "B1", "B2", "群馬", "埼玉", "東京", "静岡", "愛知", "三重", "福井", "滋賀", "大阪", "兵庫", "徳島", "香川", "岡山", "広島", "山口", "福岡", "佐賀", "長崎", "艇番", "登板", "年齢", "体重", "全国勝率", "全国2率", "当地勝率", "当地2率", "モーターNO", "モーター2率", "ボートNO", "ボート2率", "A1", "A2", "B1", "B2", "群馬", "埼玉", "東京", "静岡", "愛知", "三重", "福井", "滋賀", "大阪", "兵庫", "徳島", "香川", "岡山", "広島", "山口", "福岡", "佐賀", "長崎"]

train_days_start = datetime.date(2021, 5, 2)
train_days_end = datetime.date(2020, 4, 2)
train_days = (train_days_start - train_days_end).days + 1

# train_days_startから始まって、(train_days)日分の結果ファイルを読み込みcsvファイル化
for i in tqdm(range(train_days)):
    day = train_days_start.strftime("%Y%m%d")
    train_days_start = train_days_start - datetime.timedelta(days=1)
    read_before_file(day[2:] + ".TXT", column)

