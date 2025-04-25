import tkinter as tk
import os
import importlib

# 從 cogs 資料夾匯入 App 類別
from cogs.app import App

def load_extensions():
    """載入所有指令檔案 (cogs 資料夾中的 .py 檔案)"""
    cogs_path = "./cogs"
    if os.path.exists(cogs_path):
        for filename in os.listdir(cogs_path):
            if filename.endswith(".py") and filename != "app.py":  # 排除 app.py，避免重複載入
                module_name = f"cogs.{filename[:-3]}"
                try:
                    importlib.import_module(module_name)
                    print(f"目前載入檔案 --> {filename}")
                except Exception as e:
                    print(f"載入檔案 {filename} 時發生錯誤: {e}")
    else:
        print(f"資料夾 {cogs_path} 不存在，無法載入指令檔案。")

if __name__ == '__main__':
    # 載入 cogs 資料夾中的模組
    load_extensions()
    # 啟動主應用程式
    root = tk.Tk()
    App(root)
    root.mainloop()
