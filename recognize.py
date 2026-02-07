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

last_status = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    temp_img = "temp.jpg"
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
        status = f"Authorized: {name}"
        event = "authorized"
        color = (0, 255, 0)
    else:
        status = "INTRUDER"
        event = "intruder"
        color = (0, 0, 255)

    # Send event only if status changed
    if event != last_status:
        try:
            requests.post(SERVER_URL, json={"event": event})
            print("Sent event:", event)
        except:
            print("Server not reachable")

        last_status = event

    cv2.putText(frame, status, (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow("Access Control", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
