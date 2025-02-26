import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print('無法開啟鏡頭')
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print('無法讀取影像')
        break

    cv2.imshow('Wecam', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()