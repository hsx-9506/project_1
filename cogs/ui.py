from tkinter import ttk, StringVar, Label, Canvas

def setup_ui(window, app):
    """設定 UI 元素"""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#252526")
    style.configure("TLabel", background="#252526", foreground="white", font=("Microsoft JhengHei", 14, "bold"))
    style.configure("Rounded.TButton", background="#3e3e3e", foreground="white", 
                    font=("Microsoft JhengHei", 12, "bold"), padding=10, borderwidth=0, relief="flat")
    style.map("Rounded.TButton", background=[("active", "#505050")])

    # 主視窗佈局：左邊影像、右邊控制
    video_frame   = ttk.Frame(window, style="TFrame")
    control_frame = ttk.Frame(window, style="TFrame", width=200)
    video_frame.grid  (row=1, column=0, padx=10, pady=10, sticky="nsew")
    control_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ns")
    window.grid_rowconfigure(1, weight=1)
    window.grid_columnconfigure(0, weight=3)
    window.grid_columnconfigure(1, weight=1)

    # 影像區域
    canvas = Canvas(video_frame, bg="#1e1e1e", highlightthickness=0, borderwidth=0)
    canvas.pack(fill="both", expand=True)

    # 將 control_frame 分成四個 Labelframe
    results_frame = ttk.Labelframe(control_frame, text="Results", style="TFrame")
    cam_frame     = ttk.Labelframe(control_frame, text="Camera",  style="TFrame")
    mode_frame    = ttk.Labelframe(control_frame, text="Mode",    style="TFrame")
    misc_frame    = ttk.Labelframe(control_frame, text="Others",  style="TFrame")
    # 前三個區塊從上往下排列
    results_frame.pack(fill="x", pady=5)
    cam_frame.pack(fill="x", pady=5)
    mode_frame.pack(fill="x", pady=5)
    # Others 區塊固定在底部
    misc_frame.pack(fill="x", side="bottom", pady=5)

    # 【Results 區】顯示左右手結果
    left_hand_label    = Label(results_frame, text="左手比的數字：", bg="#252526", fg="white", font=("Microsoft JhengHei",14,"bold"))
    left_hand_label.pack(anchor="w", pady=2)
    left_hand_text     = StringVar()
    left_hand_display  = Label(results_frame, textvariable=left_hand_text, bg="#252526", fg="white", font=("Microsoft JhengHei",12))
    left_hand_display.pack(anchor="w", pady=2)

    right_hand_label   = Label(results_frame, text="右手比的數字：", bg="#252526", fg="white", font=("Microsoft JhengHei",14,"bold"))
    right_hand_label.pack(anchor="w", pady=2)
    right_hand_text    = StringVar()
    right_hand_display = Label(results_frame, textvariable=right_hand_text, bg="#252526", fg="white", font=("Microsoft JhengHei",12))
    right_hand_display.pack(anchor="w", pady=2)

    # 【Camera 區】切換攝影機按鈕
    switch_button = ttk.Button(cam_frame, text="切換攝影機 (C)", style="Rounded.TButton", command=app.switch_camera)
    switch_button.pack(fill="x", padx=5, pady=5)

    # 【Mode 區】顯示 & 切換模式
    mode_label = Label(mode_frame, text="目前模式：數字辨識模式", bg="#252526", fg="lightgreen", font=("Microsoft JhengHei",12))
    mode_label.pack(anchor="w", pady=5)
    mode_button= ttk.Button(mode_frame, text="切換模式 (M)", style="Rounded.TButton", command=app.switch_mode)
    mode_button.pack(fill="x", padx=5, pady=5)

    # 【Others 區】退出按鈕
    exit_button = ttk.Button(misc_frame, text="退出", style="Rounded.TButton", command=app.on_closing)
    exit_button.pack(fill="x", padx=5, pady=10, side="bottom")

    return {
        "canvas":           canvas,
        "left_hand_text":   left_hand_text,
        "right_hand_text":  right_hand_text,
        "mode_label":       mode_label,
        "left_hand_label":  left_hand_label,
        "right_hand_label": right_hand_label
    }
