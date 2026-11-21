import os
import time
import streamlit as st
import datetime
import cv2


RECORD_DIR = "recordings"
MIN_AREA = 1500          # ignore changes smaller than this (pixels), tune to taste
POST_MOTION_SEC = 3      # keep recording this long after motion stops
FPS = 20

os.makedirs(RECORD_DIR, exist_ok=True)

st.title("Motion Detector")
col_start, col_stop = st.columns(2)
start_camera = col_start.button("Start Camera")
stop_camera = col_stop.button("Stop Camera")
fr_slot = st.empty()
status = st.empty()

# Clicking "Stop Camera" reruns the script. That interrupts the running loop
# (the finally block releases the camera) and this run doesn't start the camera.
if stop_camera:
    st.info("Camera stopped")
elif start_camera:
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        camera.release()
        st.error("Could not open the camera (index 0). Check that it is connected and not used by another app.")
    else:
        writer = None
        last_motion = 0.0
        prev_gray = None
        try:
            while True:
                ret, frame = camera.read()
                if not ret:
                    st.error("Lost the camera feed while reading frames.")
                    break

                # Motion detection runs on the raw frame, before the clock overlay is drawn
                gray = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (21, 21), 0)
                moving = []
                if prev_gray is not None:
                    diff = cv2.absdiff(prev_gray, gray)
                    mask = cv2.dilate(cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1], None, iterations=2)
                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    moving = [c for c in contours if cv2.contourArea(c) > MIN_AREA]
                prev_gray = gray
                now = time.time()

                for c in moving:
                    x, y, w, h = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                if moving:
                    last_motion = now
                    if writer is None:
                        h, w = frame.shape[:2]
                        name = os.path.join(RECORD_DIR, datetime.datetime.now().strftime("motion_%Y%m%d_%H%M%S.avi"))
                        writer = cv2.VideoWriter(name, cv2.VideoWriter_fourcc(*"MJPG"), FPS, (w, h))
                        if writer.isOpened():
                            status.warning(f"Motion detected - recording to {name}")
                        else:
                            writer = None
                            status.error(f"Motion detected, but the video file could not be created: {name}")

                current_date = datetime.datetime.now()

                current_week_day = current_date.strftime("%A")
                cv2.putText(
                    frame,
                    current_week_day,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )

                current_time = current_date.strftime("%H:%M:%S")
                cv2.putText(
                    frame,
                    current_time,
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    1,
                    cv2.LINE_AA
                )

                # Write while recording, stop after the quiet period
                if writer is not None:
                    writer.write(frame)
                    if now - last_motion > POST_MOTION_SEC:
                        writer.release()
                        writer = None
                        status.info("Motion ended - clip saved")
                elif not moving:
                    status.empty()

                fr_slot.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        finally:
            # Runs when the feed fails, the loop breaks, or Streamlit stops the run
            if writer is not None:
                writer.release()   # save the clip if the run is stopped mid-motion
            camera.release()
