import streamlit as st
import pandas as pd
import time
import os
import platform
import cv2
import pytesseract
import numpy as np
from pyzbar.pyzbar import decode

# Setup
output_dir = "images"
excel_file = "product_data.xlsx"
os.makedirs(output_dir, exist_ok=True)

# Tesseract path
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
else:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# Init Excel
if not os.path.exists(excel_file):
    df = pd.DataFrame(columns=["Timestamp", "Image", "Price", "OCR_Text", "Barcode"])
    df.to_excel(excel_file, index=False)

st.title("📸 Product OCR + Barcode Extractor")

frame = st.camera_input("Capture Product Image")

price = st.text_input("Enter Product Price (Optional if OCR finds it)")

if frame is not None and st.button("Save with OCR + Barcode"):
    ts = int(time.time())
    image_name = f"product_{ts}.png"
    image_path = os.path.join(output_dir, image_name)

    # Save image
    with open(image_path, "wb") as f:
        f.write(frame.getbuffer())

    # Decode image
    image = cv2.imdecode(np.frombuffer(frame.getvalue(), np.uint8), cv2.IMREAD_COLOR)

    # OCR
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ocr_text = pytesseract.image_to_string(gray).strip()

    # Extract ₹ price from OCR if not provided
    import re
    match = re.search(r"₹\s?(\d+)", ocr_text)
    auto_price = f"₹{match.group(1)}" if match else ""
    final_price = price if price else auto_price if auto_price else "Not found"

    # Barcode extraction
    decoded_objects = decode(image)
    barcode = decoded_objects[0].data.decode("utf-8") if decoded_objects else "Not found"

    # Save entry
    df = pd.read_excel(excel_file)
    df.loc[len(df)] = [ts, image_path, final_price, ocr_text, barcode]
    df.to_excel(excel_file, index=False)

    st.success(f"✅ Saved with OCR & Barcode: Price={final_price}, Barcode={barcode}")

# Show table
if os.path.exists(excel_file):
    st.subheader("📊 Logged Entries")
    df = pd.read_excel(excel_file)
    st.dataframe(df)

    with open(excel_file, "rb") as f:
        st.download_button("📥 Download Excel", f, "product_data.xlsx")
