import streamlit as st
import pandas as pd
import time
import os

# Excel file setup
excel_file = "product_data.xlsx"
if not os.path.exists(excel_file):
    df = pd.DataFrame(columns=["Timestamp", "Image", "Price"])
    df.to_excel(excel_file, index=False)

st.title("📸 Product Capture App with Manual Price Entry")

# Input from webcam
frame = st.camera_input("Take a product photo")

# Price input
price = st.text_input("Enter product price (e.g., ₹1499)")

# Save button
if frame is not None and price and st.button("Save Entry"):
    ts = int(time.time())
    image_name = f"product_{ts}.png"

    # Save image
    with open(image_name, "wb") as f:
        f.write(frame.getbuffer())

    # Append to Excel
    df = pd.read_excel(excel_file)
    df.loc[len(df)] = [ts, image_name, price]
    df.to_excel(excel_file, index=False)

    st.success(f"✅ Saved: {image_name} at {price}")

# Show Excel contents
if os.path.exists(excel_file):
    st.subheader("📊 Logged Entries")
    df = pd.read_excel(excel_file)
    st.dataframe(df)

    # Download option
    with open(excel_file, "rb") as f:
        st.download_button(
            label="📥 Download Excel",
            data=f,
            file_name="product_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
