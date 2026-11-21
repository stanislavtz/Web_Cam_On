import streamlit as st
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
            fr_slot.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    except KeyboardInterrupt:
        st.error("Could not start camera.")
    finally:
        camera.release()
