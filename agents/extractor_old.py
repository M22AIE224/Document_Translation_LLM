import fitz
import os
from openai import OpenAI

with open('data/api_key.txt') as f:
    os.environ["OPENAI_API_KEY"] = f.read().strip()

# OpenAI client
client = OpenAI()

class PDFExtractor:

    def extract(self, pdf_path):
        doc = fitz.open(pdf_path)

        blocks = []
        images = []
        tables = []
        page_sizes = {}

        for page_num, page in enumerate(doc, start=1):

            w, h = page.rect.width, page.rect.height
            page_sizes[page_num] = (w, h)

            # ---------------------------------------
            # 1️⃣ Try digital text blocks
            # ---------------------------------------
            digital_blocks = []
            raw_blocks = page.get_text("blocks") or []

            for b in raw_blocks:
                block_type = b[5]
                if block_type != 0:
                    continue

                x0, y0, x1, y1 = b[0], b[1], b[2], b[3]
                text = b[4] or ""

                if text.strip():
                    digital_blocks.append({
                        "page": page_num,
                        "bbox": [x0, y0, x1 - x0, y1 - y0],
                        "text": text.strip()
                    })

            # ---------------------------------------
            # 2️⃣ Detect scanned page → use AI OCR
            # ---------------------------------------
            is_scanned = (
                len(digital_blocks) == 0 or
                (len(digital_blocks) == 1 and len(digital_blocks[0]["text"].split("\n")) <= 2)
            )

            if is_scanned:
                print(f"[AI OCR] Page {page_num} → Using GPT-4o Vision")

                pix = page.get_pixmap(dpi=200)
                img_bytes = pix.tobytes("png")

                # Call OpenAI Vision for OCR
                ocr_text = self._run_ai_ocr(img_bytes)

                # Convert OCR into blocks
                y_pos = 50
                for line in ocr_text.split("\n"):
                    line = line.strip()
                    if not line:
                        continue

                    blocks.append({
                        "page": page_num,
                        "bbox": [50, y_pos, w - 100, 20],
                        "text": line
                    })
                    y_pos += 22

            else:
                blocks.extend(digital_blocks)

            # ---------------------------------------
            # 3️⃣ Extract IMAGES normally
            # ---------------------------------------
            image_list = page.get_images(full=True)
            for idx, img in enumerate(image_list):
                xref = img[0]
                base = doc.extract_image(xref)
                img_data = base["image"]

                img_path = f"uploads/extracted_{page_num}_{idx}.png"
                os.makedirs("uploads", exist_ok=True)
                with open(img_path, "wb") as f:
                    f.write(img_data)

                for inst in page.get_image_info(xref):
                    x, y, x2, y2 = inst["bbox"]
                    images.append({
                        "page": page_num,
                        "bbox": [x, y, x2 - x, y2 - y],
                        "image_file": img_path
                    })

        return {
            "blocks": blocks,
            "images": images,
            "tables": tables,
            "page_sizes": page_sizes
        }

    # --------------------------------------------------------
    # AI OCR using GPT-4o Vision (no poppler, no tesseract)
    # --------------------------------------------------------
    def _run_ai_ocr(self, img_bytes):
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract all text from this image. Keep lines as-is."},
                            {"type": "image", "image": img_bytes}
                        ]
                    }
                ]
            )
            return resp.choices[0].message.content
        except Exception as e:
            print("AI OCR error:", e)
            return ""
