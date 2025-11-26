from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfdoc import PDFDocument
PDFDocument.forcePDFEncryption = False




class PDFRebuilder:

    def __init__(self, page_sizes):
        self.page_sizes = page_sizes
        # --- CONFIG: point to a Devanagari-capable TTF in your repo
        DEVANAGARI_TTF = os.path.join("fonts", "NotoSansDevanagari-Regular.ttf")  # <- put file here
        FALLBACK_TTF = os.path.join("fonts","NotoSansDevanagari-VariableFont_wdth,wght.ttf")  # optional fallback ttf for general unicode (set if you have one)


        # Register fonts (only if files exist)
        DEVANAGARI_FONT = None
        if os.path.isfile(DEVANAGARI_TTF):
            try:
                pdfmetrics.registerFont(TTFont("NotoDeva", DEVANAGARI_TTF))
                DEVANAGARI_FONT = "NotoDeva"
            except Exception as e:
                print(f"Exception while registering font : {e}")
                DEVANAGARI_FONT = None

        # register any fallback TrueType if provided
        if FALLBACK_TTF and os.path.isfile(FALLBACK_TTF):
            try:
                pdfmetrics.registerFont(TTFont("FallbackUnicode", FALLBACK_TTF))
                FALLBACK_FONT = "FallbackUnicode"
                
            except Exception:
                FALLBACK_FONT = "Helvetica"
        else:
            FALLBACK_FONT = "Helvetica"

        print(f"DEVANAGARI_FONT : {DEVANAGARI_FONT}")
        print(f"FALLBACK_FONT : {FALLBACK_FONT}")

        self.font_to_use = DEVANAGARI_FONT or FALLBACK_FONT

        print(f"font_to_use : {self.font_to_use}")

    def _draw_images(self, c, images, page_num, page_width, page_height):
        from reportlab.lib.utils import ImageReader

        for img in images:
            if img.get("page") != page_num:
                continue

            bbox = img.get("bbox")

            # ---------------------------------------------------------
            # CASE 1 — BBOX PRESENT → draw at exact location
            # ---------------------------------------------------------
            if bbox and len(bbox) == 4:
                try:
                    x, y, w, h = bbox
                    draw_y = page_height - y - h
                    c.drawImage(ImageReader(img["image_file"]),
                                x, draw_y, width=w, height=h, mask="auto")
                except Exception as e:
                    print("Image draw failed with bbox:", e)
                continue

            # ---------------------------------------------------------
            # CASE 2 — NO BBOX → place image in consistent safe default
            # ---------------------------------------------------------
            try:
                c.drawImage(
                    ImageReader(img["image_file"]),
                    page_width - 150,
                    page_height - 150,
                    width=140,
                    height=100,
                    mask="auto"
                )
            except Exception as e:
                print("Image draw failed without bbox:", e)

    def rebuild(self, output_path, blocks, images, tables):
        from reportlab.lib.utils import ImageReader

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

                # CASE 1 — no bbox (default positioning)
                if not bbox or len(bbox) != 4:
                    try:
                        c.drawImage(
                            ImageReader(img["image_file"]),
                            page_width - 150,
                            page_height - 150,
                            width=140,
                            height=100,
                            mask="auto",
                        )
                    except Exception as e:
                        print("Image draw failed (no bbox):", e)
                    continue

                # CASE 2 — draw with real bbox
                try:
                    x, y, w, h = bbox
                    ry = page_height - y - h
                    c.drawImage(
                        ImageReader(img["image_file"]),
                        x,
                        ry,
                        width=w,
                        height=h,
                        mask="auto",
                    )
                except Exception as e:
                    print("Image draw failed with bbox:", e)

            # ---------------- Tables ----------------
            for tbl in tables:
                if tbl.get("page") != pnum:
                    continue

                bbox = tbl.get("bbox")
                if not bbox or len(bbox) != 4:
                    print("Skipping table with invalid bbox:", bbox)
                    continue

                x0, y0, x1, y1 = bbox
                w = x1 - x0
                h = y1 - y0
                ry = page_height - y0 - h

                col_widths = tbl.get("col_widths")

                try:
                    if col_widths:
                        t = Table(tbl["data"], colWidths=col_widths)
                    else:
                        t = Table(tbl["data"])
                        
                    t.setStyle(
                        TableStyle(
                            [
                                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                                ("FONTSIZE", (0, 0), (-1, -1), 8),
                                ("FONTNAME", (0, 0), (-1, -1), self.font_to_use)
                            ]
                        )
                    )
                    t.wrapOn(c, w, h)
                    t.drawOn(c, x0, ry)
                except Exception as e:
                    print("Table draw failed:", e)

            # ---------------- Text blocks ----------------
            for blk in blocks:
                if blk.get("page") != pnum:
                    continue

                bbox = blk.get("bbox")
                if not bbox or len(bbox) != 4:
                    print("Skipping text block with invalid bbox:", bbox)
                    continue

                x, y, w, h = bbox
                ry = page_height - y - h

                c.setFont(self.font_to_use, 9)
                for line in blk["text"].split("\n"):
                    try:
                        c.drawString(x, ry, line)
                    except:
                        safe = line.encode("utf-8", "replace").decode("utf-8")
                        c.drawString(x, ry, safe)
                    ry -= 12


            c.showPage()

        c.save()
        return output_path
