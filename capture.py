import cv2, json
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk
with open("setting.json", 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

video_source = jdata["video_source"]

def open_video_source(config):

    cap = None

    if isinstance(config, str) and config.startswith("http"):
        cap = cv2.VideoCapture(config)
        if cap.isOpened():
            print(f"已使用網路串流 {config}\n")
            return cap
        else:
            cap.release
            print(f"無法開啟網路串流，改為USB攝影機 {config}\n")

    cap = cv2.VideoCapture(1)
    if cap.isOpened():
        print("已開啟USB攝影機，索引 1 \n")
        return cap
    else:
        cap.release
        raise ValueError("網路串流與USB攝影機(索引1)均無法開啟\n")

class App:
    def __init__(self, window, video_source):
        self.window = window
        self.window.title("MediaPipe 手部追蹤")
        self.video_source = video_source

        # 開啟攝影機
        self.cap = open_video_source(self.video_source)
        if not self.cap or not self.cap.isOpened():
            raise ValueError(f"無法開啟視訊來源 {self.video_source}\n")

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

    def detect_number(self, hand_landmarks, handedness):
        count = 0
        # 非拇指手指
        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]
        for tip, pip in zip(finger_tips, finger_pips):
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                count += 1

        # 判斷拇指根據 handedness
        if handedness == "Right":
            if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
                count += 1
        elif handedness == "Left":
            if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x:
                count += 1

        return count

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            # 將影像從 BGR 轉為 RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 使用 MediaPipe 進行手部偵測
            results = self.hands.process(image)
            number_text = ""
            if results.multi_hand_landmarks and results.multi_handedness:
                # 逐一處理每一隻手
                for handLms, handLabel in zip(results.multi_hand_landmarks, results.multi_handedness):
                    # 取得 handedness label ( "Left" 或 "Right" )
                    label = handLabel.classification[0].label
                    self.mp_draw.draw_landmarks(image, handLms, self.mp_hands.HAND_CONNECTIONS)
                    number = self.detect_number(handLms, label)
                    number_text += f"{label}: {number}\n"
            # 將處理後的影像轉為 PIL 影像，再轉為 ImageTk 格式供 Tkinter 顯示
            img = Image.fromarray(image)
            self.photo = ImageTk.PhotoImage(image=img)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            # 在畫布左上角顯示手勢識別的數字與左右手標籤
            self.canvas.create_text(10, 20, anchor=tk.NW, text=number_text, fill="red", font=("Arial", 20))
        self.window.after(self.delay, self.update)

    def on_closing(self):
        if self.cap.isOpened():
            self.cap.release()
        self.window.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    App(root, video_source)
