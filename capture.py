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
        self.window.title("MediaPipe 手部追蹤 - DroidCam USB")
        self.video_source = video_source

        # 開啟攝影機（使用 USB 模式虛擬攝影機）
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
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

        # 設定每隔 5 毫秒更新影像
        self.delay = 5
        self.update()

        # 設定視窗關閉事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(image)
            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(image, handLms, self.mp_hands.HAND_CONNECTIONS)
            img = Image.fromarray(image)
            self.photo = ImageTk.PhotoImage(image=img)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.window.after(self.delay, self.update)

    def on_closing(self):
        if self.cap.isOpened():
            self.cap.release()
        self.window.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    App(root, video_source)
