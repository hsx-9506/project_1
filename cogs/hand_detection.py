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
        """計算手比的數字"""
        count = 0
        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]
        for tip, pip in zip(finger_tips, finger_pips):
            if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
                count += 1

        thumb_tip = hand_landmarks.landmark[4]
        thumb_ip = hand_landmarks.landmark[3]
        if is_right and thumb_tip.x < thumb_ip.x:
            count += 1
        elif not is_right and thumb_tip.x > thumb_ip.x:
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