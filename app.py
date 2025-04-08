import streamlit as st
import cv2
from cvzone.HandTrackingModule import HandDetector
from PIL import Image
import numpy as np

st.set_page_config(page_title="Barcode/QR Scanner", layout="centered")
st.title("📷 Real-time Barcode/QR Code Scanner (No Pyzbar)")

frame_placeholder = st.image([])

start = st.button("Start Scanning")
detector = cv2.QRCodeDetector()

if start:
    cap = cv2.VideoCapture(0)
    st.info("Hold a QR/Barcode in front of the camera")

    scanned = False
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.error("Could not access webcam.")
            break

        data, bbox, _ = detector.detectAndDecode(frame)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if bbox is not None:
            for i in range(len(bbox)):
                cv2.line(frame_rgb, tuple(bbox[i][0]), tuple(bbox[(i + 1) % len(bbox)][0]), (0, 255, 0), 2)
            if data and not scanned:
                st.success(f"✅ Detected: {data}")
                scanned = True

        frame_placeholder.image(frame_rgb)

        if scanned:
            break

    cap.release()
