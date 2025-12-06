import cv2
import mediapipe as mp
from pythonosc import udp_client
import math

ip = "127.0.0.1"
port = 7001

osc_client = udp_client.SimpleUDPClient(ip, port)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Initialize webcam
cap = cv2.VideoCapture(0)

def calc_distance(p1, p2):
    """Calculate Euclidean distance between two points"""
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def check_hand_open(landmarks):
    fingers_extended = 0
    
    # Check thumb
    if landmarks[4].x < landmarks[3].x:  # Thumb pointing left
        fingers_extended += 1
    
    # Check other fingers
    finger_tips = [8, 12, 16, 20]
    finger_pips = [6, 10, 14, 18]
    
    for tip, pip in zip(finger_tips, finger_pips):
        if landmarks[tip].y < landmarks[pip].y:
            fingers_extended += 1
    
    return 1 if fingers_extended >= 4 else 0

print("Starting hand gesture tracking... Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # video processing and frame setup
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            landmarks = hand_landmarks.landmark
            
            palm_x = landmarks[9].x 
            palm_y = (1 - landmarks[9].y) * 10 # inverse for more intuitive controls
            
            # Pinch strength (distance between thumb tip and index tip)
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            pinch_dist = calc_distance(thumb_tip, index_tip)
            pinch_strength = max(0, 1 - (pinch_dist * 5))  # Inverted and scaled
            
            # Hand open/closed
            hand_open = check_hand_open(landmarks)
            
            # Send OSC messages
            osc_client.send_message("/vol/1", palm_y)
            osc_client.send_message("/toggle/2", hand_open)
            osc_client.send_message("/pitch/3", pinch_strength)
            
            # Display for debugging
            cv2.putText(frame, f"Palm X: {palm_x:.2f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Palm Y: {palm_y:.2f}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Pinch: {pinch_strength:.2f}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Open: {hand_open}", (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    cv2.imshow('Hand Gesture Control', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()