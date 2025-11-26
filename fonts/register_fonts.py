import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_NAME = "NotoDeva"

def register_indic_fonts():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_path = os.path.join(base_dir, "fonts", "NotoSansDevanagari-Regular.ttf")

    print("FONT PATH:", font_path)

    if not os.path.isfile(font_path):
        print("ERROR: Font file not found:", font_path)
        return None

    try:
        pdfmetrics.registerFont(TTFont(FONT_NAME, font_path))
        print("SUCCESS: Registered font:", FONT_NAME)
        return FONT_NAME
    except Exception as e:
        print("FONT LOAD ERROR:", e)
        return None
