import cv2
import mediapipe as mp
import os
import time

# Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

print("=== HAND SHUTDOWN CONTROL STARTED ===")
print("1. Show 5 FINGERS and HOLD 3 seconds = PC will shutdown in 10 sec")
print("2. To CANCEL shutdown, press 'c' or run 'shutdown /a' in cmd")
print("3. Press 'q' to EXIT program")
print("=====================================")

five_fingers_time = 0
is_shutdown_started = False

while True:
    success, frame = cap.read()
    if not success:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    finger_list = []
    count = 0

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Get all points
            points = []
            for id, lm in enumerate(hand_landmarks.landmark):
                x = int(lm.x * w)
                y = int(lm.y * h)
                points.append([id, x, y])

            # Check fingers open or not
            if len(points) != 0:
                if points[20][2] < points[18][2]: finger_list.append(1)
                else: finger_list.append(0)
                if points[16][2] < points[14][2]: finger_list.append(1)
                else: finger_list.append(0)
                if points[12][2] < points[10][2]: finger_list.append(1)
                else: finger_list.append(0)
                if points[8][2] < points[6][2]: finger_list.append(1)
                else: finger_list.append(0)
                if points[4][1] > points[2][1]: finger_list.append(1)
                else: finger_list.append(0)

                count = sum(finger_list)
                
                # Show count on screen
                cv2.putText(frame, f'Fingers: {count}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

                # LOGIC: 5 fingers = shutdown
                if count == 5 and not is_shutdown_started:
                    if five_fingers_time == 0:
                        five_fingers_time = time.time()
                    
                    held_time = time.time() - five_fingers_time
                    cv2.putText(frame, f'Hold: {int(held_time)}/3 sec', (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
                    
                    if held_time > 3:
                        print(">>> 5 Fingers detected! Shutting down in 10 seconds...")
                        os.system('shutdown /s /t 10')
                        is_shutdown_started = True
                        cv2.putText(frame, 'SHUTDOWN STARTED!', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
                else:
                    five_fingers_time = 0

                print(f"Fingers: {count}")

    cv2.imshow("Shutdown Control", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("Exiting program...")
        break
    if key == ord('c'):
        if is_shutdown_started:
            os.system('shutdown /a')
            print("Shutdown CANCELLED!")
            is_shutdown_started = False
            five_fingers_time = 0

cap.release()
cv2.destroyAllWindows()

# Auto cancel if you exit the program
if is_shutdown_started:
    os.system('shutdown /a')
    print("Program closed - Shutdown cancelled.")