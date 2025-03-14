import cv2
import json

# 讀取設定檔案
with open(".vscode/setting.json", 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

video_sources = [0, jdata["video_source"]]

def open_video_source(index):
    """開啟指定的攝影機來源"""
    cap = cv2.VideoCapture(video_sources[index])
    if cap.isOpened():
        print(f"已開啟攝影機: {video_sources[index]}")
        return cap
    else:
        cap.release()
        raise ValueError(f"無法開啟攝影機: {video_sources[index]}")