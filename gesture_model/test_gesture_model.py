import cv2
import mediapipe as mp
import numpy as np
import json
from tensorflow.keras.models import load_model

# 🔹 載入訓練好的 AI 模型
model = load_model("gesture_model.h5")

# 🔹 載入手勢標籤對應表
with open("gesture_labels.json", "r") as f:
    gesture_labels = json.load(f)

# 🔹 設定攝影機（0 = USB 相機，1 = 其他相機）
cap = cv2.VideoCapture(0)

# 🔹 初始化 MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

def predict_gesture(hand_landmarks):
    """使用 AI 模型預測手勢"""
    landmarks = []
    for lm in hand_landmarks.landmark:
        landmarks.extend([lm.x, lm.y])

    data = np.array(landmarks).reshape(1, 42)
    prediction = model.predict(data)[0]
    top_index = np.argmax(prediction)
    confidence = prediction[top_index]

    if confidence >= 0.7:
        return f"{gesture_labels[top_index]} ({confidence*100:.1f}%)"
    else:
        return "Uncertain 🤔"

print("📢 Press 'Q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to capture image")
        break

    # 轉換顏色 BGR → RGB（MediaPipe 需要 RGB）
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_image)

    # 如果偵測到手
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # 取得預測手勢
            gesture = predict_gesture(hand_landmarks)

            # 顯示結果
            cv2.putText(frame, gesture, (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # 顯示影像
    cv2.putText(frame, "Press 'Q' to quit", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.imshow("Hand Gesture Recognition", frame)

    # 按 Q 鍵離開
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 釋放攝影機 & 關閉視窗
cap.release()
cv2.destroyAllWindows()
