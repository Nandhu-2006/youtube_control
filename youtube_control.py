import cv2
import mediapipe as mp
import pyautogui
import time

# MediaPipe setup - works for 0.10.21
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Only 1 hand, confidence 70%
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

# To prevent pressing key many times
last_action_time = 0
cooldown = 1.0 # 1 second cooldown

print("Starting... Open YouTube and show your hand to camera")
print("5 fingers = Play/Pause (k)")
print("1 finger = Forward 10s (l)")
print("2 fingers = Backward 10s (j)")
print("3 fingers = Volume Up")
print("4 fingers = Volume Down")
print("Press ESC to exit")

while True:
    success, frame = cap.read()
    if not success:
        continue

    # Flip for mirror effect
    frame = cv2.flip(frame, 1)
    f_h, f_w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    lm_list = []

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            for id, lm in enumerate(hand_landmarks.landmark):
                x = int(lm.x * f_w)
                y = int(lm.y * f_h)
                lm_list.append([id, x, y])

    finger_count = 0
    if len(lm_list)!= 0:
        # 4 fingers (index to pinky) - check if tip is above pip joint
        # y is smaller when finger is up
        fingers = []
        # Tip ids: 8, 12, 16, 20 | Pip ids: 6, 10, 14, 18
        if lm_list[8][2] < lm_list[6][2]:
            fingers.append(1)
        else:
            fingers.append(0)
        if lm_list[12][2] < lm_list[10][2]:
            fingers.append(1)
        else:
            fingers.append(0)
        if lm_list[16][2] < lm_list[14][2]:
            fingers.append(1)
        else:
            fingers.append(0)
        if lm_list[20][2] < lm_list[18][2]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Thumb - check x position (for right hand)
        if lm_list[4][1] > lm_list[2][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        finger_count = sum(fingers)

    # Show count on screen
    cv2.putText(frame, f'Fingers: {finger_count}', (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Only press if cooldown finished
    current_time = time.time()
    if current_time - last_action_time > cooldown:
        if finger_count == 5:
            pyautogui.press('k')
            print("Play/Pause")
            last_action_time = current_time
        elif finger_count == 1:
            pyautogui.press('l')
            print("Forward 10s")
            last_action_time = current_time
        elif finger_count == 2:
            pyautogui.press('j')
            print("Backward 10s")
            last_action_time = current_time
        elif finger_count == 3:
            pyautogui.press('up')
            print("Volume Up")
            last_action_time = current_time
        elif finger_count == 4:
            pyautogui.press('down')
            print("Volume Down")
            last_action_time = current_time

    cv2.imshow("YouTube Gesture Control", frame)

    # Press ESC to quit
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()