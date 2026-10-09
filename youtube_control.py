import cv2
import mediapipe as mp
import pyautogui
import time

# Setup MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# To avoid repeat actions
last_action_time = 0
cooldown = 1.0 # 1 sec gap

cap = cv2.VideoCapture(0)

print("Camera Started - Show hand gestures")
print("Press ESC or 'q' to stop")

try:
    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1) # mirror
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        fingers_up = 0

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Count fingers
                tips = [4, 8, 12, 16, 20]
                # Thumb
                if hand_landmarks.landmark[tips[0]].x > hand_landmarks.landmark[tips[0]-1].x:
                    fingers_up += 1
                # Other 4 fingers
                for i in range(1, 5):
                    if hand_landmarks.landmark[tips[i]].y < hand_landmarks.landmark[tips[i]-2].y:
                        fingers_up += 1

        # Action with cooldown
        current_time = time.time()
        if current_time - last_action_time > cooldown:
            if fingers_up == 1:
                pyautogui.press('right') # Forward 10s
                print("Forward 10s")
                last_action_time = current_time
            elif fingers_up == 2:
                pyautogui.press('left') # Backward 10s
                print("Backward 10s")
                last_action_time = current_time
            elif fingers_up == 3:
                pyautogui.press('up') # Volume Up
                print("Volume Up")
                last_action_time = current_time
            elif fingers_up == 4:
                pyautogui.press('down') # Volume Down
                print("Volume Down")
                last_action_time = current_time
            elif fingers_up == 5:
                pyautogui.press('space') # Play/Pause
                print("Play/Pause")
                last_action_time = current_time

        cv2.putText(frame, f'Fingers: {fingers_up}', (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, 'ESC/q to exit', (10, 470),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        cv2.imshow("YouTube Control", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'): # 27 = ESC
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Camera Released - Program Stopped")