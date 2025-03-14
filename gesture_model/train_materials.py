import cv2
import mediapipe as mp
import pandas as pd
import os

# 🔹 設定攝影機（0 為 USB 攝影機，1 為次選）
cap = cv2.VideoCapture(0)

# 🔹 初始化 MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# 🔹 設定手勢名稱（請修改成你要收集的手勢）
gesture_name = "palm"

# 🔹 儲存資料的陣列
collected_data = []

# 🔹 創建存放資料的資料夾
data_folder = "gesture_data"
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

print(f"📢 Collecting gesture [{gesture_name}], press 'S' to save, 'Q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to capture image")
        break

    # 轉換顏色 BGR → RGB（MediaPipe 需要 RGB）
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_image)

    # 如果有偵測到手
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # 提取 21 個關鍵點 (x, y)
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y])

            cv2.putText(frame, f"Collected: {len(collected_data)}", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # 顯示即時影像
    cv2.putText(frame, "Press 'S' to save, 'Q' to quit", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.imshow("Gesture Collection", frame)

    key = cv2.waitKey(1)
    if key == ord('s'):
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.extend([lm.x, lm.y])

                collected_data.append(landmarks + [gesture_name])
                print(f"✅ Saved data {len(collected_data)} ({gesture_name})")

    elif key == ord('q'):
        break

# 釋放攝影機 & 關閉視窗
cap.release()
cv2.destroyAllWindows()

# 儲存為 CSV
csv_path = os.path.join(data_folder, f"{gesture_name}.csv")
df = pd.DataFrame(collected_data)
df.to_csv(csv_path, index=False)

print(f"📁 {gesture_name}.csv saved to 【{data_folder}】! Total {len(collected_data)} samples.")
