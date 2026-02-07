import cv2
import os
import requests
from deepface import DeepFace

SERVER_URL = "http://localhost:5000/event"

# Load known faces
known_faces_dir = "known_faces"
known_images = []

for file in os.listdir(known_faces_dir):
    if file.endswith(".jpg") or file.endswith(".png"):
        known_images.append(os.path.join(known_faces_dir, file))

print("Loaded authorized faces:", known_images)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.putText(frame, "Press SPACE to scan face", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Access Control", frame)

    key = cv2.waitKey(1)

    # SPACE pressed
    if key == 32:
        print("Capturing face...")

        temp_img = "captured.jpg"
        cv2.imwrite(temp_img, frame)

        recognized = False
        name = "Intruder"

        for img_path in known_images:
            try:
                result = DeepFace.verify(
                    img1_path=temp_img,
                    img2_path=img_path,
                    enforce_detection=False,
                    model_name="Facenet"
                )

                if result["verified"]:
                    name = os.path.basename(img_path).split(".")[0]
                    recognized = True
                    break

            except:
                pass

        if recognized:
            print("Authorized:", name)
            event = "authorized"
            image_path = None
        else:
            print("INTRUDER DETECTED")
            event = "intruder_detected"
            image_path = "static/captured.jpg"
            cv2.imwrite(image_path, frame)

        # Send event to server
        try:
            requests.post(SERVER_URL, json={
                "event": event,
                "image": image_path
                })
            print("Event sent:", event)
        except:
            print("Server not reachable")

    # ESC to exit
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
