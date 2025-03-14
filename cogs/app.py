import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from cogs.video import open_video_source
from cogs.ui import setup_ui
from cogs.hand_detection import HandDetection
import cv2

class App:
    def __init__(self, window):
        # 初始化主視窗
        self.window = window
        self.window.title("🖐 手勢數字 & AI 手勢識別")
        self.window.configure(bg="#1e1e1e")

        # 初始化變數
        self.is_advanced_mode = False  # 模式切換標誌
        self.hand_detection = HandDetection()  # Mediapipe 手部偵測
        self.cap = open_video_source(0)  # 開啟攝影機

        # 根據攝影機影像大小設定視窗大小
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # 取得影像寬度
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 取得影像高度
        self.window.geometry(f"{self.width + 200}x{self.height + 50}")  # 加上額外空間以容納控制區域

        # 設定 UI
        self.ui_elements = setup_ui(window, self)  # 使用外部函數設定 UI

        # 啟動影像更新
        self.delay = 5
        self.update()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            left_result, right_result, processed_frame = self.hand_detection.process_frame(frame, self.is_advanced_mode)
            self.ui_elements["left_hand_text"].set(left_result)
            self.ui_elements["right_hand_text"].set(right_result)

            # 更新影像到 Canvas
            image = Image.fromarray(processed_frame)
            photo = ImageTk.PhotoImage(image=image)
            if hasattr(self, "canvas_image"):
                self.ui_elements["canvas"].delete(self.canvas_image)
            self.canvas_image = self.ui_elements["canvas"].create_image(0, 0, image=photo, anchor=tk.NW)
            self.ui_elements["canvas"].image = photo

        self.window.after(self.delay, self.update)

    def switch_camera(self):
        """切換攝影機"""
        self.cap.release()
        self.cap = open_video_source((self.cap.index + 1) % len(self.cap.sources))

    def switch_mode(self):
        """切換模式"""
        self.is_advanced_mode = not self.is_advanced_mode
        mode_text = "手勢識別模式" if self.is_advanced_mode else "數字辨識模式"
        self.ui_elements["mode_label"].config(text=f"目前模式：{mode_text}")

    def on_closing(self):
        """釋放資源並關閉視窗"""
        if self.cap.isOpened():
            self.cap.release()
        self.window.destroy()