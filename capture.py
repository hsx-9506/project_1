import cv2, json
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk
with open("setting.json", 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

video_source = jdata["video_source"]

class App:
    def __init__(self, window, video_source):
        self.window = window
        self.window.title("MediaPipe 手部追蹤與手勢辨識 - DroidCam USB")
        self.video_source = video_source

        # 開啟攝影機
        self.cap = cv2.VideoCapture(self.video_source)
        if not self.cap.isOpened():
            raise ValueError("無法開啟攝影機", self.video_source)

        # 取得影像尺寸
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 建立 Tkinter Canvas 顯示影像
        self.canvas = tk.Canvas(window, width=self.width, height=self.height)
        self.canvas.pack()

        # 初始化 MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,         # 流式影像模式
            max_num_hands=2,                 # 最多偵測兩隻手
            min_detection_confidence=0.7,    # 偵測信心門檻
            min_tracking_confidence=0.5      # 追蹤信心門檻
        )
        self.mp_draw = mp.solutions.drawing_utils

        # 設定每隔 5 毫秒更新影像
        self.delay = 5
        self.update()

        # 設定視窗關閉事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    def detect_gesture(self, hand_landmarks):
        # 手指的關鍵點索引 (不包含拇指)
        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]
        count_extended = 0

        for tip, pip in zip(finger_tips, finger_pips):
            # 注意：影像中 y 值越小代表越往上
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                count_extended += 1

        # 簡單分類：全收縮為握拳，全部伸展為全開，其它視為其他手勢
        if count_extended == 0:
            return "握拳"
        elif count_extended == 4:
            return "全開"
        else:
            return "其他"

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            # 將影像從 BGR 轉為 RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 使用 MediaPipe 進行手部偵測
            results = self.hands.process(image)
            gesture_text = ""
            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    # 畫出手部關鍵點與連線
                    self.mp_draw.draw_landmarks(image, handLms, self.mp_hands.HAND_CONNECTIONS)
                    # 偵測手勢
                    gesture = self.detect_gesture(handLms)
                    gesture_text = gesture  # 目前僅處理第一隻手
                    # 你可以在這裡印出或記錄更多資訊
            # 將處理後的影像轉為 PIL 影像，再轉為 ImageTk 格式供 Tkinter 顯示
            img = Image.fromarray(image)
            self.photo = ImageTk.PhotoImage(image=img)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            # 在畫布上顯示手勢文字（左上角）
            self.canvas.create_text(10, 20, anchor=tk.NW, text=gesture_text, fill="red", font=("Arial", 20))
        self.window.after(self.delay, self.update)

    def on_closing(self):
        if self.cap.isOpened():
            self.cap.release()
        self.window.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    App(root, video_source)
