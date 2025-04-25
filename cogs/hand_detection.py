import cv2, json
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model

model = load_model("gesture_model/gesture_model.h5")
gesture_labels = ["victory ✌️", "fist ✊", "ok 👌", "middle 🖕", "thumbs_up 👍", "heart 🫰"]

class HandDetection:
    def __init__(self):
        # 初始化 Mediapipe 和模型
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=2,
                                         min_detection_confidence=0.7, min_tracking_confidence=0.5)
        self.mp_draw = mp.solutions.drawing_utils
        self.model = load_model("gesture_model/gesture_model.h5")
        with open(".vscode/gesture_labels.json", "r", encoding='utf8') as f:
            self.gesture_labels = json.load(f)

    def process_frame(self, frame, is_advanced_mode):
        """處理影像並進行手勢辨識"""
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image)

        left_result, right_result = "未偵測", "未偵測"
        if results.multi_hand_landmarks and results.multi_handedness:
            for handLms, handLabel in zip(results.multi_hand_landmarks, results.multi_handedness):
                label = handLabel.classification[0].label  # Left or Right
                if is_advanced_mode:
                    result = self.predict_gesture(handLms)
                else:
                    result = self.detect_number(handLms, label == "Right")

                if label == "Left":
                    left_result = result
                elif label == "Right":
                    right_result = result

                self.mp_draw.draw_landmarks(image, handLms, self.mp_hands.HAND_CONNECTIONS)

        return left_result, right_result, image

    
    def detect_number(self, hand_landmarks, is_right):
        """計算手比的數字 (前/後翻 + 左右手正確的拇指判斷)"""
        count = 0
        # 1. 食指～小指伸直判斷
        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]
        for tip, pip in zip(finger_tips, finger_pips):
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                count += 1

        # 2. 掌面朝向偵測 (cross product)
        w = hand_landmarks.landmark[0]   # Wrist
        i = hand_landmarks.landmark[5]   # Index_MCP
        p = hand_landmarks.landmark[17]  # Pinky_MCP
        v1 = np.array([ i.x - w.x,  i.y - w.y ])
        v2 = np.array([ p.x - w.x,  p.y - w.y ])
        cross_z = v1[0]*v2[1] - v1[1]*v2[0]

        # 右手、左手分別取不同條件
        if is_right:
            palm_facing = (cross_z > 0)   # 右手：cross_z>0 表示掌面朝前
        else:
            palm_facing = (cross_z < 0)   # 左手：cross_z<0 表示掌面朝前

        # 3. 拇指伸出判斷
        thumb_tip = hand_landmarks.landmark[4]
        thumb_ip  = hand_landmarks.landmark[3]

        if is_right:
            # 右手：掌面朝前時 tip.x < ip.x；掌背朝前時反向
            if (palm_facing     and thumb_tip.x < thumb_ip.x) \
            or (not palm_facing and thumb_tip.x > thumb_ip.x):
                count += 1
        else:
            # 左手：掌面朝前時 tip.x > ip.x；掌背朝前時反向
            if (palm_facing     and thumb_tip.x > thumb_ip.x) \
            or (not palm_facing and thumb_tip.x < thumb_ip.x):
                count += 1

        return count

    def predict_gesture(self, hand_landmarks):
        """使用模型預測手勢"""
        landmarks = []
        for lm in hand_landmarks.landmark:
            landmarks.extend([lm.x, lm.y])
        data = np.array(landmarks).reshape(1, 42)
        prediction = self.model.predict(data)[0]
        top_index = np.argmax(prediction)
        confidence = prediction[top_index]
        if confidence >= 0.7:
            return f"{self.gesture_labels[top_index]} ({confidence*100:.1f}%)"
        else:
            return "不確定 🤔"