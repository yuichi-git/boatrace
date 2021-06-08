import urllib.request #ファイルダウンロードし、解凍する
import lhafile
import os
import numpy as np
import csv
import datetime
from tqdm import tqdm

def unzip(lzh_save_dir_path, txt_save_dir_path):
    files = os.listdir(lzh_save_dir_path)
    for filename in files:
        if filename.endswith(".lzh"):
            txt_file = lhafile.Lhafile(lzh_save_dir_path + filename)
            info = txt_file.infolist()
            name = info[0].filename
            open(txt_save_dir_path + name, "wb").write(txt_file.read(name))

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

def download_result_file(yyyymmdd, save_dir_path):
    yyyymm = yyyymmdd[0:6]
    yymmdd = yyyymmdd[2:8]
    url = "http://www1.mbrace.or.jp/od2/K/" + yyyymm + "/k" + yymmdd + ".lzh"
    save_filename = os.path.basename(url)
    save_file_path = save_dir_path + save_filename
    try:
        with urllib.request.urlopen(url) as web_file, open(save_file_path, "wb") as local_file:
            local_file.write(web_file.read())
    except urllib.error.URLError as e:
        print(e)

before_lzh_save_dir_path = "./before_download/"
before_txt_save_dir_path = "./before_txtfile/"

result_lzh_save_dir_path = "./result_download/"
result_txt_save_dir_path = "./result_txtfile/"

train_days_start = datetime.date(2020, 5, 2)
train_days_end = datetime.date(2020, 4, 2)
train_days = (train_days_start - train_days_end).days + 1

for i in tqdm(range(train_days)):
    day = train_days_start.strftime("%Y%m%d")
    train_days_start = train_days_start - datetime.timedelta(days=1)
    download_result_file(day, result_lzh_save_dir_path)
    download_before_file(day, before_lzh_save_dir_path)
    unzip(result_lzh_save_dir_path, result_txt_save_dir_path)
    unzip(before_lzh_save_dir_path, before_txt_save_dir_path)