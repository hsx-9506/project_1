import os
import pandas as pd
# import numpy as np
import json
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.utils import to_categorical

# 🔹 設定手勢數據資料夾
data_folder = "gesture_data"

# 🔹 讀取所有 CSV 檔案
all_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]

# 🔹 合併所有手勢數據
data_list = []
for file in all_files:
    df = pd.read_csv(os.path.join(data_folder, file))
    data_list.append(df)

# 🔹 合併為一個 DataFrame
data = pd.concat(data_list, ignore_index=True)

# 🔹 分割特徵 (X) 和標籤 (y)
X = data.iloc[:, :-1].values  # 取所有座標 (x, y)
y = data.iloc[:, -1].values   # 取標籤

# 🔹 轉換標籤為數字（不區分左右手）
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

# 🔹 轉換為 One-hot 編碼
y = to_categorical(y)

# 🔹 分割訓練集與測試集 (80% 訓練，20% 測試)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 🔹 構建 MLP 神經網絡模型
model = Sequential([
    Dense(128, activation="relu", input_shape=(X.shape[1],)),
    Dropout(0.2),
    Dense(64, activation="relu"),
    Dropout(0.2),
    Dense(y.shape[1], activation="softmax")  # 輸出層
])

model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

# 🔹 訓練模型
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))

# 🔹 儲存模型
model.save("gesture_model.h5")

# 🔹 儲存標籤對應
with open("gesture_labels.json", "w") as f:
    json.dump(label_encoder.classes_.tolist(), f)

# 🔹 評估模型準確率
loss, accuracy = model.evaluate(X_test, y_test)
print(f"🎯 Test Accuracy: {accuracy * 100:.2f}%")

print("✅ Model training complete! Model saved as 'gesture_model.h5'.")
print("✅ Gesture labels saved as 'gesture_labels.json'.")
