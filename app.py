import streamlit as st
import cv2
from PIL import Image
import numpy as np
import zbarlight
import requests
import time

st.set_page_config(page_title="Barcode Scanner", layout="centered")
st.title("📦 Barcode Scanner with Product Details")

FRAME_WINDOW = st.image([])
start_camera = st.button("Start Scanning")
scanned = set()


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


def scan_codes(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    pil_img = Image.fromarray(gray)

    codes = zbarlight.scan_codes('ean13', pil_img)  # or 'code128', 'qrcode' as needed
    if codes:
        code = codes[0].decode("utf-8")
        if code not in scanned:
            scanned.add(code)
            st.success(f"🔍 Detected Barcode: `{code}`")
            fetch_product_details(code)
            return True
    return False


if start_camera:
    cap = cv2.VideoCapture(0)
    st.info("📸 Scanning started... Hold a barcode in front of the camera.")

    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("Webcam access failed.")
            break

        found = scan_codes(frame)
        FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if found:
            st.info("✅ Barcode scanned. Closing camera...")
            time.sleep(2)
            break

    cap.release()
