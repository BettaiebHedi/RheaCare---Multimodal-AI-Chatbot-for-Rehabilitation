import cv2
import mediapipe as mp
import numpy as np
import time

# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Function to calculate the angle between three points
def calculate_angle(a, b, c):
    ab = np.array(a) - np.array(b)
    bc = np.array(c) - np.array(b)
    radians = np.arctan2(np.linalg.det([ab, bc]), np.dot(ab, bc))
    return np.abs(np.degrees(radians))

# Compare landmarks from webcam and reference video frame
def compare_hand_poses(webcam_landmarks, video_landmarks):
    feedback = []
    correct = True

    if webcam_landmarks and video_landmarks:
        # Extract key points for wrist, index finger tip, and middle finger tip
        def extract_points(landmarks):
            return {
                "wrist": [landmarks.landmark[mp_hands.HandLandmark.WRIST].x,
                          landmarks.landmark[mp_hands.HandLandmark.WRIST].y],
                "index_tip": [landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x,
                              landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y],
                "middle_tip": [landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x,
                               landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y]
            }

        webcam_points = extract_points(webcam_landmarks)
        video_points = extract_points(video_landmarks)

        # Calculate angles for comparison
        webcam_angle = calculate_angle(webcam_points["wrist"], webcam_points["index_tip"], webcam_points["middle_tip"])
        video_angle = calculate_angle(video_points["wrist"], video_points["index_tip"], video_points["middle_tip"])

        # Compare angles with a threshold
        if abs(webcam_angle - video_angle) > 10:  # 10-degree threshold
            feedback.append("Hand posture is incorrect. Adjust your fingers.")
            correct = False
        else:
            feedback.append("Hand posture is correct!")

    if correct:
        feedback.append("Exercise is correct!")
    else:
        feedback.append("Exercise needs improvement.")

    return feedback

# Function to calculate the Mean Absolute Error (MAE) between predicted and ground truth landmarks
def calculate_mae(predicted_landmarks, ground_truth_landmarks):
    errors = []
    for i in range(len(predicted_landmarks)):
        pred = np.array([predicted_landmarks[i].x, predicted_landmarks[i].y])
        gt = np.array([ground_truth_landmarks[i].x, ground_truth_landmarks[i].y])
        errors.append(np.linalg.norm(pred - gt))
    return np.mean(errors)

# Load the reference video
video_path = 'video.mp4'  # Replace with your video path
video_cap = cv2.VideoCapture(video_path)

# Start webcam
webcam_cap = cv2.VideoCapture(0)

# Initialize MediaPipe Hands
with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while webcam_cap.isOpened():
        start_time = time.time()

        # Read frame from webcam
        success_webcam, webcam_frame = webcam_cap.read()
        if not success_webcam:
            print("Ignoring empty webcam frame.")
            continue

        # Read frame from video
        success_video, video_frame = video_cap.read()
        if not success_video:
            print("End of reference video reached.")
            video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop the video
            continue

        # Process webcam frame
        webcam_rgb = cv2.cvtColor(webcam_frame, cv2.COLOR_BGR2RGB)
        webcam_results = hands.process(webcam_rgb)

        # Process video frame
        video_rgb = cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB)
        video_results = hands.process(video_rgb)

        # Draw hand landmarks on both frames
        annotated_webcam = webcam_frame.copy()
        annotated_video = video_frame.copy()

        if webcam_results.multi_hand_landmarks:
            for hand_landmarks in webcam_results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(annotated_webcam, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        if video_results.multi_hand_landmarks:
            for hand_landmarks in video_results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(annotated_video, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Compare landmarks and provide feedback
        if webcam_results.multi_hand_landmarks and video_results.multi_hand_landmarks:
            feedback = compare_hand_poses(webcam_results.multi_hand_landmarks[0], video_results.multi_hand_landmarks[0])
            for i, text in enumerate(feedback):
                cv2.putText(annotated_webcam, text, (10, 30 + i * 30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)

            # Calculate Mean Absolute Error (MAE) for evaluation
            mae = calculate_mae(webcam_results.multi_hand_landmarks[0].landmark, video_results.multi_hand_landmarks[0].landmark)
            cv2.putText(annotated_webcam, f"MAE: {mae:.4f}", (10, 120), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)

        # Measure processing time and display FPS
        end_time = time.time()
        fps = 1 / (end_time - start_time)
        cv2.putText(annotated_webcam, f"FPS: {fps:.2f}", (10, 90), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2)

        # Show both video and webcam feeds
        cv2.imshow('Webcam Feed', annotated_webcam)
        cv2.imshow('Reference Video', annotated_video)

        # Exit on pressing 'Esc'
        if cv2.waitKey(5) & 0xFF == 27:
            break

# Release resources
webcam_cap.release()
video_cap.release()
cv2.destroyAllWindows()