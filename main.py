import streamlit as st
import datetime
import cv2

st.title("Motion Detector")
start_camera = st.button("Start Camera")
fr_slot = st.empty()

if start_camera:
    camera = cv2.VideoCapture(0)
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                st.error("Could not read from camera")
                break

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

            fr_slot.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    except KeyboardInterrupt:
        st.error("Could not start camera.")
    finally:
        camera.release()
