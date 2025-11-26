print("\n==============================")
print("REBUILDER MODULE STARTING LOAD")
print("==============================")

import traceback

try:
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os
    from fonts.register_fonts import FONT_NAME as INDIC_FONT


    print("rebuilder.py loaded. Classes:", [name for name in dir() if "Rebuilder" in name])


    
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
    
    #class PDFRebuilder:
    class PDFBuilder:

        def __init__(self, page_sizes):
            self.page_sizes = page_sizes

        def rebuild(self, output_path, blocks, images, tables):

            print("Available fonts:", pdfmetrics.getRegisteredFontNames())
            print("Using font:", INDIC_FONT)
            c = canvas.Canvas(output_path)

            max_page = max(self.page_sizes.keys())

            for pnum in range(1, max_page + 1):
                page_width, page_height = self.page_sizes[pnum]
                c.setPageSize((page_width, page_height))

                # ---------------- Images ----------------
                for img in images:
                    if img["page"] != pnum:
                        continue

                    bbox = img.get("bbox")
                    if not bbox:
                        # Place at default top-right if no bbox
                        c.drawImage(
                            ImageReader(img["image_file"]),
                            page_width - 150,
                            page_height - 150,
                            width=140,
                            height=100,
                            mask="auto"
                        )
                        continue

                    # Draw with bbox
                    x, y, w, h = bbox
                    ry = page_height - y - h
                    c.drawImage(
                        ImageReader(img["image_file"]),
                        x, ry,
                        width=w, height=h,
                        mask="auto"
                    )

                # ---------------- Tables ----------------
                for tbl in tables:
                    if tbl["page"] != pnum:
                        continue

                    x0, y0, x1, y1 = tbl["bbox"]
                    w = x1 - x0
                    h = y1 - y0
                    ry = page_height - y0 - h

                    t = Table(tbl["data"])
                    t.setStyle(TableStyle([
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                        ("FONTSIZE", (0, 0), (-1, -1), 8)
                    ]))
                    t.wrapOn(c, w, h)
                    t.drawOn(c, x0, ry)

                # ---------------- Text Blocks ----------------
                for blk in blocks:
                    if blk["page"] != pnum:
                        continue

                    x, y, w, h = blk["bbox"]
                    ry = page_height - y - h

                    # Set the Devanagari font
                    c.setFont(INDIC_FONT, 10)

                    for line in blk["text"].split("\n"):
                        c.drawString(x, ry, line)
                        ry -= 12

                c.showPage()

            c.save()
            return output_path


except Exception as e:
    print("\n🔥🔥 ERROR LOADING REBUILDER.PY 🔥🔥")
    print("Exception:", e)
    traceback.print_exc()