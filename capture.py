import cv2, json
import mediapipe as mp
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tensorflow.keras.models import load_model
import numpy as np

# 讀取設定
with open(".vscode/setting.json", 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

# 讀取手勢識別模型
model = load_model("gesture_model.h5")
gesture_labels = ["victory ✌️", "fist ✊", "ok 👌", "middle 🖕", "thumbs_up 👍", "heart 🤏"]

# 預設使用 USB 攝影機 (0)，若無法開啟則改用串流
video_sources = [0, jdata["video_source"]]
current_camera = 0

# 開啟攝影機
def open_video_source(index):
    cap = cv2.VideoCapture(video_sources[index])
    if cap.isOpened():
        print(f"已開啟攝影機: {video_sources[index]}\n")
        return cap
    else:
        cap.release()
        raise ValueError(f"無法開啟攝影機: {video_sources[index]}")

class App:
    def __init__(self, window):
        self.window = window
        self.window.title("🖐 手勢數字 & AI 手勢識別")
        self.window.configure(bg="#1e1e1e")

        self.model = load_model("gesture_model.h5")
        with open(".vscode/gesture_labels.json", "r", encoding='utf8') as f:
            self.gesture_labels = json.load(f)

        global current_camera
        self.cap = open_video_source(current_camera)

        # 設定 UI 風格
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#252526")  
        style.configure("TLabel", background="#252526", foreground="white", font=("Microsoft JhengHei", 14, "bold"))
        style.configure("Rounded.TButton", background="#3e3e3e", foreground="white", 
                        font=("Microsoft JhengHei", 12, "bold"), padding=10, borderwidth=0, relief="flat")
        style.map("Rounded.TButton", background=[("active", "#505050")])  

        # 主要 UI 佈局
        self.video_frame = tk.Frame(window, bg="#1e1e1e")
        self.control_frame = tk.Frame(window, bg="#252526", width=200)

        self.video_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.control_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ns")

        window.grid_rowconfigure(1, weight=1)
        window.grid_columnconfigure(0, weight=3)  
        window.grid_columnconfigure(1, weight=1)  

        # 影像顯示區
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.canvas = tk.Canvas(self.video_frame, width=self.width, height=self.height, bg="#1e1e1e",
                                highlightthickness=0, borderwidth=0)  
        self.canvas.pack(fill="both", expand=True)  

        # 左手顯示區
        self.left_hand_label = tk.Label(self.control_frame, text="左手比的數字：", font=("Microsoft JhengHei", 14, "bold"), 
                                        bg="#252526", fg="white")
        self.left_hand_label.pack(pady=5)
        self.left_hand_text = tk.StringVar()
        self.left_hand_display = tk.Label(self.control_frame, textvariable=self.left_hand_text, font=("Microsoft JhengHei", 12), 
                                          bg="#252526", fg="white")
        self.left_hand_display.pack(pady=5)

        # 右手顯示區
        self.right_hand_label = tk.Label(self.control_frame, text="右手比的數字：", font=("Microsoft JhengHei", 14, "bold"), 
                                         bg="#252526", fg="white")
        self.right_hand_label.pack(pady=5)
        self.right_hand_text = tk.StringVar()
        self.right_hand_display = tk.Label(self.control_frame, textvariable=self.right_hand_text, font=("Microsoft JhengHei", 12), 
                                           bg="#252526", fg="white")
        self.right_hand_display.pack(pady=5)

        # 按鈕區
        self.switch_button = ttk.Button(self.control_frame, text="切換攝影機 (C)", style="Rounded.TButton", command=self.switch_camera)
        self.switch_button.pack(pady=10)

        self.mode_label = tk.Label(self.control_frame, text="目前模式：數字辨識模式", font=("Microsoft JhengHei", 12),
                                   bg="#252526", fg="lightgreen")
        self.mode_label.pack(pady=10)
        self.mode_button = ttk.Button(self.control_frame, text="切換模式 (M)", 
                                      style="Rounded.TButton", command=self.switch_mode)
        self.mode_button.pack(pady=5)

        self.exit_button = ttk.Button(self.control_frame, text="退出", style="Rounded.TButton", command=self.on_closing)
        self.exit_button.pack(pady=10)

        # 變數
        self.is_advanced_mode = False
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=2,
                                         min_detection_confidence=0.7, min_tracking_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils

        self.delay = 5
        self.update()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.window.bind("<c>", lambda event: self.switch_camera())
        self.window.bind("<m>", lambda event: self.switch_mode())

    def detect_number(self, hand_landmarks, is_right):
        """計算手比的數字 (包含拇指)"""
        count = 0
        finger_tips = [8, 12, 16, 20]  # 食指～小指
        finger_pips = [6, 10, 14, 18]
        for tip, pip in zip(finger_tips, finger_pips):
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                count += 1

        # **拇指判定**
        thumb_tip = hand_landmarks.landmark[4]
        thumb_ip = hand_landmarks.landmark[3]

        if is_right and thumb_tip.x < thumb_ip.x:
            count += 1
        elif not is_right and thumb_tip.x > thumb_ip.x:
            count += 1

        return count
    
    def predict_gesture(self, hand_landmarks):
        """使用 AI 模型預測手勢"""
        landmarks = []
        for lm in hand_landmarks.landmark:
            landmarks.extend([lm.x, lm.y])

        # 轉換為 NumPy 陣列並進行預測
        data = np.array(landmarks).reshape(1, 42)
        prediction = self.model.predict(data)[0]
        
        # 取得機率最高的手勢
        top_index = np.argmax(prediction)
        confidence = prediction[top_index]

        if confidence >= 0.7:
            return f"{self.gesture_labels[top_index]} ({confidence*100:.1f}%)"
        else:
            return "不確定 🤔"

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(image)

            left_result, right_result = "未偵測", "未偵測"

            if results.multi_hand_landmarks and results.multi_handedness:
                for handLms, handLabel in zip(results.multi_hand_landmarks, results.multi_handedness):
                    label = handLabel.classification[0].label  # Left or Right
                    
                    # 根據模式選擇數字識別或 AI 手勢識別
                    if self.is_advanced_mode:
                        result = self.predict_gesture(handLms)  # 使用 AI 手勢識別
                    else:
                        result = str(self.detect_number(handLms, label == "Right"))  # 使用數字辨識

                    # 根據手的類型（左 / 右）來更新結果
                    if label == "Left":
                        left_result = result
                    elif label == "Right":
                        right_result = result

                    self.mp_draw.draw_landmarks(image, handLms, self.mp_hands.HAND_CONNECTIONS)

            self.left_hand_text.set(left_result)
            self.right_hand_text.set(right_result)

            self.photo = ImageTk.PhotoImage(image=Image.fromarray(image))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(self.delay, self.update)

    def switch_camera(self):
        global current_camera
        current_camera = (current_camera + 1) % len(video_sources)
        self.cap.release()
        self.cap = open_video_source(current_camera)

    def switch_mode(self):
        """切換模式，並修改 UI 文字"""
        self.is_advanced_mode = not self.is_advanced_mode
        mode_text = "手勢識別模式" if self.is_advanced_mode else "數字辨識模式"
        self.mode_label.config(text=f"目前模式：{mode_text}")

        # 修改 UI 文字
        if self.is_advanced_mode:
            self.left_hand_label.config(text="左手的手勢：")
            self.right_hand_label.config(text="右手的手勢：")
        else:
            self.left_hand_label.config(text="左手比的數字：")
            self.right_hand_label.config(text="右手比的數字：") 

    def on_closing(self):
        if self.cap.isOpened():
            self.cap.release()
        self.window.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    App(root)
    root.mainloop()
