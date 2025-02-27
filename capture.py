import cv2, json
import mediapipe as mp
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont

with open("setting.json", 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

video_source = jdata["video_source"]

def open_video_source(config):
    """嘗試使用設定的視訊來源，優先使用網路串流，失敗則回退至 USB 攝影機 (索引 1)"""
    cap = None
    if isinstance(config, str) and config.startswith("http"):
        cap = cv2.VideoCapture(config)
        if cap.isOpened():
            print(f"已使用網路串流 {config}\n")
            return cap
        else:
            cap.release()
            print(f"無法開啟網路串流，改為USB攝影機 {config}\n")

    cap = cv2.VideoCapture(1)
    if cap.isOpened():
        print("已開啟USB攝影機，索引 1 \n")
        return cap
    else:
        cap.release()
        raise ValueError("網路串流與USB攝影機(索引1)均無法開啟\n")

class App:
    def __init__(self, window, video_source):
        self.window = window
        self.window.title("🖐 手勢識別 - ChatGPT 深色 UI")
        self.window.configure(bg="#1e1e1e")  # 設定主背景

        self.video_source = video_source

        # **設定 UI 風格**
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#252526")
        style.configure("TLabel", background="#252526", foreground="white", font=("Helvetica", 14))
        style.configure("Rounded.TButton", background="#3e3e3e", foreground="white", font=("Helvetica", 12),
                        padding=10, borderwidth=0, relief="flat")
        style.map("Rounded.TButton", background=[("active", "#505050")])

        # **標題區域**
        self.header_frame = tk.Frame(window, bg="#252526", height=50, padx=15, pady=5, relief="flat")
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

        # **標題文字**
        self.title_label = tk.Label(self.header_frame, text="手部識別", font=("Helvetica", 14, "bold"),
                                    bg="#252526", fg="white", anchor="w")
        self.title_label.pack(side="left", fill="x", expand=True)

        # **主要區域**
        self.video_frame = tk.Frame(window, bg="#1e1e1e")
        self.control_frame = tk.Frame(window, bg="#252526", width=200)

        self.video_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.control_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        window.grid_rowconfigure(1, weight=1)
        window.grid_columnconfigure(0, weight=3)
        window.grid_columnconfigure(1, weight=1)

        # **影像區域**
        self.cap = open_video_source(self.video_source)
        if not self.cap or not self.cap.isOpened():
            raise ValueError(f"無法開啟視訊來源 {self.video_source}\n")

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.canvas = tk.Canvas(self.video_frame, width=self.width, height=self.height, bg="#1e1e1e",
                                highlightthickness=0, borderwidth=0)  
        self.canvas.pack()

        # **控制區域**
        self.status_label = ttk.Label(self.control_frame, text="狀態：運行中")
        self.status_label.pack(pady=10)

        self.exit_button = ttk.Button(self.control_frame, text="退出", style="Rounded.TButton", command=self.on_closing)
        self.exit_button.pack(pady=10)

        # **MediaPipe 設定**
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False, max_num_hands=2,
            min_detection_confidence=0.7, min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

        self.delay = 5
        self.update()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def detect_number(self, hand_landmarks, handedness):
        """計算伸展手指的數量"""
        count = 0
        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]
        for tip, pip in zip(finger_tips, finger_pips):
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                count += 1
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
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(image)
            number_text = ""
            if results.multi_hand_landmarks and results.multi_handedness:
                for handLms, handLabel in zip(results.multi_hand_landmarks, results.multi_handedness):
                    label = handLabel.classification[0].label
                    self.mp_draw.draw_landmarks(image, handLms, self.mp_hands.HAND_CONNECTIONS)
                    number = self.detect_number(handLms, label)
                    number_text += f"{label}: {number}\n"

            # **美化文字**
            img = Image.fromarray(image)
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", 26)
            except IOError:
                font = ImageFont.load_default()
            text_position = (20, 20)
            draw.text((text_position[0]+2, text_position[1]+2), number_text, font=font, fill="black")
            draw.text(text_position, number_text, font=font, fill="white")

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
    root.mainloop()
