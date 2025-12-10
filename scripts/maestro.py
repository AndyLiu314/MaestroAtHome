import cv2
import mediapipe as mp
from pythonosc import udp_client
import math

ip = "127.0.0.1"
port = 7001
osc_client = udp_client.SimpleUDPClient(ip, port)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)

def calc_distance(p1, p2):
    """Calculate Euclidean distance between two points"""
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def check_hand_open(landmarks):
    fingers_extended = 0
    if landmarks[4].x < landmarks[3].x:
        fingers_extended += 1
    for tip, pip in zip([8,12,16,20],[6,10,14,18]):
        if landmarks[tip].y < landmarks[pip].y:
            fingers_extended += 1
    return 1 if fingers_extended >= 4 else 0

print("Starting hand gesture tracking...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            
            hand_label = results.multi_handedness[idx].classification[0].label  # "Left" or "Right"
            landmarks = hand_landmarks.landmark
            
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Tracking for hand position (x, y)
            palm_left = -((landmarks[9].x - 0.5) * 20)
            palm_right = (landmarks[9].x - 0.5) * 20
            palm_y = (1 - landmarks[9].y) * 15

            # Distances for pinch (between thumb and index)
            pinch_dist = calc_distance(landmarks[4], landmarks[8])
            pinch_strength = (max(0, 1 - (pinch_dist * 5))) * 3

            # LEFT HAND LOGIC: Only checks for open or closed fist, triggers envelope
            if hand_label == "Left":
                hand_open = check_hand_open(landmarks)
                osc_client.send_message("/toggle/2", hand_open)

                cv2.putText(frame, "LEFT HAND", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 0), 2)
                cv2.putText(frame, f"Open: {hand_open}", (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # RIGHT HAND LOGIC: all other gesture controls
            if hand_label == "Right":
                osc_client.send_message("/vol/1", palm_y)
                osc_client.send_message("/pitch/3", pinch_strength)
                osc_client.send_message("/pan_left/4", palm_left)
                osc_client.send_message("/pan_right/5", palm_right)

                cv2.putText(frame, "RIGHT HAND", (10, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 0), 2)
                cv2.putText(frame, f"Palm Left: {palm_left:.2f}", (10, 150),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Palm Right: {palm_right:.2f}", (10, 180),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Palm Y: {palm_y:.2f}", (10, 210),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Pinch: {pinch_strength:.2f}", (10, 240),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    display = cv2.resize(frame, None, fx=1.5, fy=1.5)
    cv2.imshow('Hand Gesture Control', display)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
