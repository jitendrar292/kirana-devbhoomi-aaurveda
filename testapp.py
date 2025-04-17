import cv2
import pytesseract
import platform
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.graphics.texture import Texture
from kivy.clock import Clock
import pandas as pd
import re
import time
import os

# ─── Configure Tesseract path based on OS ──────────────────────────────────────
if platform.system() == "Windows":
    # 1) Download & install Tesseract for Windows:
    #    https://github.com/tesseract-ocr/tesseract/releases
    # 2) During install note the path (usually "C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
    # 3) Make sure that folder is in your PATH, OR uncomment & set below:
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
else:
    # On Linux (including WSL) install via:
    # sudo apt update && sudo apt install -y tesseract-ocr
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# ─── Excel file setup ─────────────────────────────────────────────────────────
excel_file = "product_data.xlsx"
if not os.path.exists(excel_file):
    df = pd.DataFrame(columns=["Timestamp", "Image", "ExtractedText", "Price"])
    df.to_excel(excel_file, index=False)

# ─── Kivy App ────────────────────────────────────────────────────────────────
class CamApp(App):
    def build(self):
        self.capture = cv2.VideoCapture(0)
        layout = BoxLayout(orientation="vertical")

        self.img_widget = Image()
        layout.add_widget(self.img_widget)

        btn = Button(text="Capture & Extract", size_hint=(1, 0.15))
        btn.bind(on_press=self.capture_image)
        layout.add_widget(btn)

        # update at ~30 FPS
        Clock.schedule_interval(self.update, 1.0 / 30.0)
        return layout

    def update(self, dt):
        ret, frame = self.capture.read()
        if not ret:
            return
        # flip & push to Kivy texture
        buf = cv2.flip(frame, 0).tobytes()    # tobytes() instead of tostring()
        tex = Texture.create(
            size=(frame.shape[1], frame.shape[0]), colorfmt="bgr"
        )
        tex.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        self.img_widget.texture = tex
        self.current_frame = frame

    def capture_image(self, instance):
        if not hasattr(self, "current_frame"):
            return
        ts = int(time.time())
        fname = f"product_{ts}.png"
        cv2.imwrite(fname, self.current_frame)

        # OCR
        gray = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray).strip()

        # price extraction
        m = re.search(r"₹\s?(\d+)", text)
        price = f"₹{m.group(1)}" if m else "Not found"

        # append to Excel
        df = pd.read_excel(excel_file)
        df.loc[len(df)] = [ts, fname, text, price]
        df.to_excel(excel_file, index=False)

        print(f"✅ Saved to {excel_file}: {fname}, Price={price}")

    def on_stop(self):
        # release camera on exit
        self.capture.release()

if __name__ == "__main__":
    CamApp().run()
