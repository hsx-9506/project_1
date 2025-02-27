import cv2, json
import mediapipe as mp
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

with open("setting.json", 'r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

video_sources = [jdata["video_source"], 1]  # 預設為網路串流，次選 USB 攝影機
current_camera = 0  # 當前攝影機索引

def open_video_source(index):
    # 嘗試使用當前索引的視訊來源
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
        self.window.title("🖐 手勢數字辨識 - 攝影機切換")
        self.window.configure(bg="#1e1e1e")  

        global current_camera
        self.cap = open_video_source(current_camera)

        # **設定 UI 風格**
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#252526")  
        style.configure("TLabel", background="#252526", foreground="white", font=("Microsoft JhengHei", 14, "bold"))
        style.configure("Rounded.TButton", background="#3e3e3e", foreground="white", 
                        font=("Microsoft JhengHei", 12, "bold"), padding=10, borderwidth=0, relief="flat")
        style.map("Rounded.TButton", background=[("active", "#505050")])  

        # **標題區域**
        self.header_frame = tk.Frame(window, bg="#252526", height=50, padx=15, pady=5, relief="flat")
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.title_label = tk.Label(self.header_frame, text="攝影機切換 & 手勢數字辨識", font=("Microsoft JhengHei", 14, "bold"),
                                    bg="#252526", fg="white", anchor="w")
        self.title_label.pack(side="left", fill="x", expand=True)

        # **主要區域**
        self.video_frame = tk.Frame(window, bg="#1e1e1e")
        self.control_frame = tk.Frame(window, bg="#252526", width=200)

        self.video_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.control_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ns")

        window.grid_rowconfigure(1, weight=1)
        window.grid_columnconfigure(0, weight=3)  
        window.grid_columnconfigure(1, weight=1)  

        # **影像區域**
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.canvas = tk.Canvas(self.video_frame, width=self.width, height=self.height, bg="#1e1e1e",
                                highlightthickness=0, borderwidth=0)  
        self.canvas.pack(fill="both", expand=True)  

        # **左右手數字辨識顯示區**
        self.left_hand_label = tk.Label(self.control_frame, text="左手比的數字：", font=("Microsoft JhengHei", 14, "bold"), 
                                        bg="#252526", fg="white")
        self.left_hand_label.pack(pady=5)
        self.left_hand_text = tk.StringVar()
        self.left_hand_display = tk.Label(self.control_frame, textvariable=self.left_hand_text, font=("Microsoft JhengHei", 12), 
                                          bg="#252526", fg="white")
        self.left_hand_display.pack(pady=5)

        self.right_hand_label = tk.Label(self.control_frame, text="右手比的數字：", font=("Microsoft JhengHei", 14, "bold"), 
                                         bg="#252526", fg="white")
        self.right_hand_label.pack(pady=5)
        self.right_hand_text = tk.StringVar()
        self.right_hand_display = tk.Label(self.control_frame, textvariable=self.right_hand_text, font=("Microsoft JhengHei", 12), 
                                           bg="#252526", fg="white")
        self.right_hand_display.pack(pady=5)

        # **按鈕**
        self.switch_button = ttk.Button(self.control_frame, text="切換攝影機 (C)", style="Rounded.TButton", command=self.switch_camera)
        self.switch_button.pack(pady=10)

        self.exit_button = ttk.Button(self.control_frame, text="退出", style="Rounded.TButton", command=self.on_closing)
        self.exit_button.pack(pady=10)

        # **MediaPipe 設定**
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=2,
                                         min_detection_confidence=0.7, min_tracking_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils

        self.delay = 5
        self.update()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # **綁定鍵盤事件 (C 鍵切換攝影機)**
        self.window.bind("<c>", lambda event: self.switch_camera())

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

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            if current_camera == 0:
                frame = cv2.flip(frame, 1)

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(image)
            left_hand_count, right_hand_count = "未偵測", "未偵測"

            if results.multi_hand_landmarks and results.multi_handedness:
                for handLms, handLabel in zip(results.multi_hand_landmarks, results.multi_handedness):
                    label = handLabel.classification[0].label  
                    count = self.detect_number(handLms, label == "Right")

                    if label == "Left":
                        left_hand_count = f"{count}"
                    elif label == "Right":
                        right_hand_count = f"{count}"

                    self.mp_draw.draw_landmarks(image, handLms, self.mp_hands.HAND_CONNECTIONS)

            self.left_hand_text.set(left_hand_count)
            self.right_hand_text.set(right_hand_count)

            self.photo = ImageTk.PhotoImage(image=Image.fromarray(image))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(self.delay, self.update)

    def switch_camera(self):
        global current_camera
        current_camera = (current_camera + 1) % len(video_sources)
        self.cap.release()
        self.cap = open_video_source(current_camera)

    def on_closing(self):
        if self.cap.isOpened():
            self.cap.release()
        self.window.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    App(root)
    root.mainloop()
