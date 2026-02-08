import cv2
import numpy as np
import requests
from datetime import datetime
import json

# Server config
SERVER_URL = "http://localhost:5000/activity"
DEVICE_ID = "camera-01"


class SimplePostureDetector:
    """
    Simple posture detector using OpenCV body part detection.
    Detects standing, sitting, or sleeping based on contour analysis.
    """
    
    def __init__(self, server_url=SERVER_URL):
        self.server_url = server_url
        self.last_activity = None
        self.activity_history = []
        self.max_history = 5
        
    def detect_posture(self, frame):
        """
        Detect posture using simple contour analysis.
        - Standing: Tall vertical contour
        - Sitting: Shorter, wider contour, centered
        - Sleeping: Very wide, low contour (person lying down)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Background subtraction / simple foreground detection
        blur = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Threshold to find body
        _, thresh = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY)
        
        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (30, 30))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) == 0:
            return "Unknown"
        
        # Get the largest contour (should be the person)
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        if area < 500:  # Too small to be a person
            return "Unknown"
        
        # Get bounding box
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Calculate aspect ratio (height / width)
        aspect_ratio = h / (w + 1e-5)
        
        # Get center of mass
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
        else:
            cx, cy = x + w // 2, y + h // 2
        
        # Heuristic-based classification
        # Standing: tall (aspect_ratio > 1.2), centered vertically
        # Sitting: medium height (0.8 < aspect_ratio < 1.2), lower in frame
        # Sleeping: wide and short (aspect_ratio < 0.8), very low in frame
        
        frame_height = frame.shape[0]
        vertical_position = cy / frame_height  # 0 = top, 1 = bottom
        
        if aspect_ratio > 1.5:
            # Tall shape
            if vertical_position < 0.6:
                return "Standing"
            else:
                return "Standing"
        elif aspect_ratio > 1.0:
            # Medium tall
            if vertical_position > 0.65:
                return "Sitting"
            else:
                return "Standing"
        elif aspect_ratio > 0.6:
            # Wider shape
            return "Sitting"
        else:
            # Very wide and short
            return "Sleeping"
    
    def smooth_prediction(self, current_activity):
        """Apply smoothing to reduce jitter"""
        self.activity_history.append(current_activity)
        if len(self.activity_history) > self.max_history:
            self.activity_history.pop(0)
        
        if self.activity_history:
            from collections import Counter
            most_common = Counter(self.activity_history).most_common(1)[0][0]
            return most_common
        return current_activity
    
    def send_activity(self, activity):
        """Send detected activity to server"""
        try:
            payload = {
                "activity": activity,
                "device_id": DEVICE_ID,
                "timestamp": datetime.utcnow().isoformat()
            }
            response = requests.post(self.server_url, json=payload, timeout=2)
            
            if response.status_code == 200:
                print(f"✓ Activity '{activity}' sent to server")
                self.last_activity = activity
                return True
            else:
                print(f"✗ Server returned {response.status_code}: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"⚠ Server unreachable. Activity not sent (offline mode)")
            return False
        except Exception as e:
            print(f"✗ Error sending activity: {e}")
            return False
    
    def process_frame(self, frame):
        """Process a video frame and detect posture"""
        # Detect posture
        current_activity = self.detect_posture(frame)
        
        # Smooth the prediction
        smoothed_activity = self.smooth_prediction(current_activity)
        
        # Send to server only if activity changed
        if self.last_activity != smoothed_activity:
            self.send_activity(smoothed_activity)
        
        # Draw info on frame
        cv2.putText(frame, f"Posture: {smoothed_activity}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
        
        cv2.putText(frame, f"Status: {self.last_activity or 'Initializing...'}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        return frame


def main():
    """Run posture detection from camera stream"""
    print("🎥 Starting Posture Detector...")
    print(f"📡 Server: {SERVER_URL}")
    print("Press 'q' to quit\n")
    
    detector = SimplePostureDetector(server_url=SERVER_URL)
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Could not open camera")
        return
    
    # Set frame properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    frame_count = 0
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            
            if not ret:
                print("❌ Failed to read frame")
                break
            
            frame_count += 1
            
            # Process every frame
            frame = detector.process_frame(frame)
            
            # Show statistics
            if frame_count % 10 == 0:
                print(f"📊 Frames processed: {frame_count} | Last activity: {detector.last_activity}")
            
            # Display the frame
            cv2.imshow("Posture Detector", frame)
            
            # Exit on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n👋 Exiting...")
                break
    
    except KeyboardInterrupt:
        print("\n⚠ Interrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("✓ Camera released")


if __name__ == "__main__":
    main()
