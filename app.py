import streamlit as st
import cv2
from pyzbar import pyzbar
import numpy as np
import requests
import time

st.set_page_config(page_title="Barcode & QR Code Scanner", layout="centered")
st.title("📦 Barcode & QR Code Scanner with Product Details")

FRAME_WINDOW = st.image([])
qr_enabled = st.checkbox("Also detect QR Codes", value=False)
start_camera = st.button("Start Scanning")

scanned = set()

def scan_codes(frame):
    decoded_objects = pyzbar.decode(frame)
    for obj in decoded_objects:
        code_data = obj.data.decode("utf-8")
        code_type = obj.type
        (x, y, w, h) = obj.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if code_data not in scanned:
            scanned.add(code_data)
            st.success(f"🔍 Detected {code_type}: `{code_data}`")

            if code_type == "QRCODE" and qr_enabled:
                st.info("This is a QR Code:")
                st.code(code_data)
            elif code_type != "QRCODE":
                fetch_product_details(code_data)

            return True  # stop scanning

    return False

def fetch_product_details(barcode):
    url = f"https://api.upcitemdb.com/prod/trial/lookup?upc={barcode}"

    try:
        response = requests.get(url)
        data = response.json()

        if "items" in data and len(data["items"]) > 0:
            item = data["items"][0]
            st.subheader("🛍 Product Info")
            st.write("**Title:**", item.get("title", "N/A"))
            st.write("**Brand:**", item.get("brand", "N/A"))
            st.write("**Category:**", item.get("category", "N/A"))
            st.write("**Description:**", item.get("description", "N/A"))

            if item.get("images"):
                st.image(item["images"][0], width=200)
        else:
            st.warning("No product details found for this barcode.")
    except Exception as e:
        st.error(f"API Error: {e}")

if start_camera:
    cap = cv2.VideoCapture(0)
    st.info("📸 Scanning started... Hold a barcode/QR code in front of the camera.")

    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("Webcam access failed.")
            break

        found = scan_codes(frame)
        FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if found:
            st.info("✅ Code scanned. Closing camera...")
            time.sleep(2)
            break

    cap.release()
