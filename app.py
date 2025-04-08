import streamlit as st
import cv2
import numpy as np
from pyzbar import pyzbar
import requests
import time

st.set_page_config(page_title="Barcode & QR Code Scanner", layout="centered")
st.title("📦 Barcode & QR Code Scanner with Product Lookup")

FRAME_WINDOW = st.image([])
start = st.button("Start Scanning")
scanned = set()


def scan_code(frame):
    decoded_objects = pyzbar.decode(frame)
    for obj in decoded_objects:
        code_data = obj.data.decode("utf-8")
        code_type = obj.type
        (x, y, w, h) = obj.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if code_data not in scanned:
            scanned.add(code_data)
            st.success(f"🔍 Detected {code_type}: `{code_data}`")

            if code_type != "QRCODE":
                fetch_product_details(code_data)
            else:
                st.info("This is a QR Code:")
                st.code(code_data)

            return True
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
        st.error(f"Error fetching details: {e}")


if start:
    cap = cv2.VideoCapture(0)
    st.info("📸 Scanning... Hold a barcode or QR in front of the webcam.")

    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("Webcam not accessible.")
            break

        found = scan_code(frame)
        FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if found:
            st.info("✅ Scan complete. Stopping camera...")
            time.sleep(2)
            break

    cap.release()
