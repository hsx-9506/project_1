from tkinter import ttk, Canvas, StringVar, Label

def setup_ui(window, app):
    """設定 UI 元素"""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#252526")
    style.configure("TLabel", background="#252526", foreground="white", font=("Microsoft JhengHei", 14, "bold"))
    style.configure("Rounded.TButton", background="#3e3e3e", foreground="white", 
                    font=("Microsoft JhengHei", 12, "bold"), padding=10, borderwidth=0, relief="flat")
    style.map("Rounded.TButton", background=[("active", "#505050")])

    # 設定主視窗的佈局
    video_frame = ttk.Frame(window, style="TFrame")
    control_frame = ttk.Frame(window, style="TFrame", width=200)

    video_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    control_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ns")

    window.grid_rowconfigure(1, weight=1)
    window.grid_columnconfigure(0, weight=3)
    window.grid_columnconfigure(1, weight=1)

    # 設定影像顯示區
    canvas = Canvas(video_frame, bg="#1e1e1e", highlightthickness=0, borderwidth=0)
    canvas.pack(fill="both", expand=True)

    # 左手顯示區
    left_hand_text = StringVar()
    left_hand_label = Label(control_frame, text="左手比的數字：", font=("Microsoft JhengHei", 14, "bold"), bg="#252526", fg="white")
    left_hand_label.pack(pady=5)
    left_hand_display = Label(control_frame, textvariable=left_hand_text, font=("Microsoft JhengHei", 12), bg="#252526", fg="white")
    left_hand_display.pack(pady=5)

    # 右手顯示區
    right_hand_text = StringVar()
    right_hand_label = Label(control_frame, text="右手比的數字：", font=("Microsoft JhengHei", 14, "bold"), bg="#252526", fg="white")
    right_hand_label.pack(pady=5)
    right_hand_display = Label(control_frame, textvariable=right_hand_text, font=("Microsoft JhengHei", 12), bg="#252526", fg="white")
    right_hand_display.pack(pady=5)

    # 控制按鈕
    switch_button = ttk.Button(control_frame, text="切換攝影機 (C)", style="Rounded.TButton", command=app.switch_camera)
    switch_button.pack(pady=10)

    mode_label = Label(control_frame, text="目前模式：數字辨識模式", font=("Microsoft JhengHei", 12), bg="#252526", fg="lightgreen")
    mode_label.pack(pady=10)
    mode_button = ttk.Button(control_frame, text="切換模式 (M)", style="Rounded.TButton", command=app.switch_mode)
    mode_button.pack(pady=5)

    exit_button = ttk.Button(control_frame, text="退出", style="Rounded.TButton", command=app.on_closing)
    exit_button.pack(pady=10)

    return {
        "canvas": canvas,
        "left_hand_text": left_hand_text,
        "right_hand_text": right_hand_text,
        "mode_label": mode_label
    }