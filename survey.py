import cv2
import torch
import threading
import queue
import time
import speech_recognition as sr
import difflib
import re
import warnings
import numpy as np

warnings.filterwarnings("ignore", category=FutureWarning)

# -------------------------
# Config
# -------------------------
CONF_THRESHOLD = 0.3
FRAME_QUEUE_MAX = 3
PROCESSED_QUEUE_MAX = 3
frames_since_seen = 0
MAX_MISS_FRAMES = 5

# -------------------------
# Globals
# -------------------------

target_object = None
tracking_active = False

frame_queue = queue.Queue(maxsize=FRAME_QUEUE_MAX)
processed_frame_queue = queue.Queue(maxsize=PROCESSED_QUEUE_MAX)
lock = threading.Lock()

# -------------------------
# Load YOLOv5
# -------------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_NAME = "yolov5s"

print(f"[INIT] device={DEVICE}, model={MODEL_NAME}")

model = torch.hub.load("ultralytics/yolov5", MODEL_NAME, verbose=False)
model.conf = CONF_THRESHOLD

if DEVICE == "cuda":
    model.to(DEVICE)

yolo_labels = [name.lower() for name in model.names.values()]

# -------------------------
# Speech Recognition
# -------------------------
recognizer = sr.Recognizer()
mic = sr.Microphone()

def extract_object_name(text):
    text = text.lower()
    if "stop" in text:
        return "STOP"
    for label in yolo_labels:
        if label in text:
            return label
    words = re.findall(r"\w+", text)
    for w in words:
        best = difflib.get_close_matches(w, yolo_labels, n=1, cutoff=0.6)
        if best:
            return best[0]
    return None

def callback(recognizer_obj, audio):
    global target_object, tracking_active
    try:
        command = recognizer_obj.recognize_google(audio).lower()
    except:
        return

    if "stop" in command:
        with lock:
            target_object = None
            tracking_active = False
        print("\n🛑 Stopped tracking.\n")
        return

    obj = extract_object_name(command)
    if obj:
        with lock:
            target_object = obj
            tracking_active = False
        print(f"\n🎯 Target set: {obj}\n")
    else:
        print(f"\n⚠ No valid object in command.\n")

# -------------------------
# YOLO helper functions
# -------------------------
def run_model_on_rgb(rgb_img):
    results = model(rgb_img)
    xyxy_np = None
    try:
        if hasattr(results, "xyxy"):
            xyxy_np = results.xyxy[0].cpu().numpy()
    except:
        try:
            df = results.pandas().xyxy[0]
            if not df.empty:
                xyxy_np = df[['xmin', 'ymin', 'xmax', 'ymax', 'confidence', 'class']].values
        except:
            return None
    return xyxy_np

def detection_matches_object(xyxy_np, obj_name):
    if xyxy_np is None:
        return None
    for det in xyxy_np:
        if len(det) < 6:
            continue
        x1, y1, x2, y2, conf, cls = det
        label = model.names[int(cls)]
        if label.lower() == obj_name.lower() and float(conf) > CONF_THRESHOLD:
            return (int(x1), int(y1), int(x2), int(y2), float(conf), int(cls))
    return None

# -------------------------
# Detection Thread
# -------------------------
def detection_loop():
    global target_object, frames_since_seen, tracking_active

    frame_counter = 0

    while True:
        try:
            frame = frame_queue.get(timeout=1)
        except queue.Empty:
            continue

        frame_counter += 1

        # run YOLO every 3 frames
        if frame_counter % 3 != 0:
            try:
                if not processed_frame_queue.full():
                    processed_frame_queue.put_nowait(frame)
            except queue.Full:
                pass
            continue

        with lock:
            obj = target_object

        if not obj:
            try:
                if not processed_frame_queue.full():
                    processed_frame_queue.put_nowait(frame)
            except:
                pass
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        xyxy_np = run_model_on_rgb(rgb)
        match = detection_matches_object(xyxy_np, obj)

        if match is not None:
            frames_since_seen = 0

            x1, y1, x2, y2, conf, cls = match
            tracking_active = True

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(frame, f"{model.names[cls]} {conf:.2f}", (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

            try:
                if not processed_frame_queue.full():
                    processed_frame_queue.put_nowait(frame)
            except:
                pass

            continue

        # NOT FOUND
        frames_since_seen += 1

        if frames_since_seen < MAX_MISS_FRAMES:
            try:
                processed_frame_queue.put_nowait(frame)
            except:
                pass
            continue

        tracking_active = False

        try:
            processed_frame_queue.put_nowait(frame)
        except:
            pass

# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    print("\n🎤 Speak: 'find person', 'find dog', etc. Say 'stop' to cancel.\n")

    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    stop_listening = recognizer.listen_in_background(mic, callback, phrase_time_limit=4)

    threading.Thread(target=detection_loop, daemon=True).start()

    cap = cv2.VideoCapture("http:/10.86.97.198:8080/video")

    if not cap.isOpened():
        print("⚠ Failed to access camera stream!")

    skip_counter = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            frame = cv2.resize(frame, (640, 480))
            skip_counter += 1

            # send every other frame to detection
            if skip_counter % 2 == 0:
                try:
                    if not frame_queue.full():
                        frame_queue.put_nowait(frame.copy())
                except:
                    pass

            # display processed frame if available
            try:
                display_frame = processed_frame_queue.get_nowait()
            except:
                display_frame = frame

            cv2.imshow("Object Detection", display_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        stop_listening(wait_for_stop=False)
        cap.release()
        cv2.destroyAllWindows()