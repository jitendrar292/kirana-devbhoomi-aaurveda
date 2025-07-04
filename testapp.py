import streamlit as st
import pandas as pd
import time
import os

# Excel setup
excel_file = "product_data.xlsx"
if not os.path.exists(excel_file):
    df = pd.DataFrame(columns=["Timestamp", "Image"])
    df.to_excel(excel_file, index=False)

st.title("📷 Product Image Capture App (No OCR)")

frame = st.camera_input("Capture product image")

if frame is not None:
    ts = int(time.time())
    filename = f"product_{ts}.png"

    # Save image to file
    with open(filename, "wb") as f:
        f.write(frame.getbuffer())

    # Save record to Excel
    df = pd.read_excel(excel_file)
    df.loc[len(df)] = [ts, filename]
    df.to_excel(excel_file, index=False)

    st.success(f"✅ Image saved as {filename} and logged to Excel.")
