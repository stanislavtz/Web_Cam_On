import streamlit as st
import time
import cv2


st.title("Motion Detector")
start_camera = st.button("Start Camera")

camera = cv2.VideoCapture(0)
time.sleep(2)

if start_camera:
    st.caption("Camera Started")
