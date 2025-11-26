import fitz
import pdfplumber
import os


class PDFBlockExtractor:

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.blocks = []
        self.images = []
        self.tables = []
        self.page_sizes = {}

    def extract(self):
        self._extract_text_blocks()
        self._extract_tables()
        self._remove_table_text_blocks()   # <--- ADD THIS LINE
        self._extract_images()

        return {
            "blocks": self.blocks,
            "images": self.images,
            "tables": self.tables,
            "page_sizes": self.page_sizes
        }

    def _remove_table_text_blocks(self):
        cleaned = []

        for blk in self.blocks:
            bx, by, bw, bh = blk["bbox"]
            block_box = (bx, by, bx + bw, by + bh)

            is_inside_table = False

            for tbl in self.tables:
                if tbl["page"] != blk["page"]:
                    continue

                tx0, ty0, tx1, ty1 = tbl["bbox"]
                table_box = (tx0, ty0, tx1, ty1)

                # Check if block is inside table box
                if (block_box[0] >= table_box[0] and
                    block_box[2] <= table_box[2] and
                    block_box[1] >= table_box[1] and
                    block_box[3] <= table_box[3]):
                    is_inside_table = True
                    break

            if not is_inside_table:
                cleaned.append(blk)

        self.blocks = cleaned

    # ------------------------------
    # TEXT BLOCKS
    # ------------------------------
    def _extract_text_blocks(self):
        with pdfplumber.open(self.pdf_path) as pdf:
            for pnum, page in enumerate(pdf.pages, start=1):
                self.page_sizes[pnum] = (page.width, page.height)

                # Get real text lines with proper bounding boxes
                lines = page.extract_text_lines()

                if not lines:
                    continue

                for line in lines:
                    text = line.get("text", "").strip()
                    if not text:
                        continue

                    x0 = line["x0"]
                    y0 = line["top"]
                    x1 = line["x1"]
                    y1 = line["bottom"]

                    self.blocks.append({
                        "page": pnum,
                        "bbox": [x0, y0, x1 - x0, y1 - y0],
                        "text": text
                    })
    # ------------------------------
    # TABLES
    # ------------------------------
    def _extract_tables(self):
        with pdfplumber.open(self.pdf_path) as pdf:
            for pnum, page in enumerate(pdf.pages, start=1):
                tables = page.find_tables()

                for tbl in tables:
                    bbox = tbl.bbox

                    col_edges = set()

                    # Extract all x0/x1 edges
                    for cell in tbl.cells:
                        try:
                            x0, x1 = self.get_x0_x1(cell)
                            col_edges.add(x0)
                            col_edges.add(x1)
                        except Exception as e:
                            print("Skipping cell:", e)
                            continue

                    col_edges = sorted(col_edges)

                    col_widths = []
                    for i in range(len(col_edges) - 1):
                        col_widths.append(col_edges[i+1] - col_edges[i])

                    self.tables.append({
                        "page": pnum,
                        "bbox": bbox,
                        "data": tbl.extract(),
                        "col_widths": col_widths,
                    })

    def get_x0_x1(self, cell):
        # Case 1: cell is a dict
        if isinstance(cell, dict):
            return cell["x0"], cell["x1"]

        # Case 2: cell is a tuple (x0, top, x1, bottom, text)
        if isinstance(cell, (list, tuple)) and len(cell) >= 3:
            return cell[0], cell[2]

        raise ValueError("Unknown cell format: " + str(cell))


    def _extract_tables_bkp(self):
        with pdfplumber.open(self.pdf_path) as pdf:
            for pnum, page in enumerate(pdf.pages, start=1):
                tables = page.find_tables()

                for tbl in tables:
                    self.tables.append({
                        "page": pnum,
                        "bbox": tbl.bbox,
                        "data": tbl.extract()
                    })

    # ------------------------------
    # IMAGES
    # ------------------------------
    def _extract_images(self):
        import fitz
        pdf = fitz.open(self.pdf_path)

        os.makedirs("processed_output/images", exist_ok=True)

        for page_index, page in enumerate(pdf, start=1):

            try:
                image_list = page.get_images(full=True)
            except Exception as e:
                print(f"Error reading images on page {page_index}: {e}")
                continue

            for img_data in image_list:

                raw_xref = img_data[0]

                # FIX 1 → Correct xref type
                try:
                    xref = int(raw_xref) if isinstance(raw_xref, (bytes, bytearray)) else raw_xref
                except:
                    print("Skipping image because xref cannot convert:", raw_xref)
                    continue

                # FIX 2 → Use ONLY extract_image (NEVER Pixmap)
                try:
                    extracted = pdf.extract_image(xref)
                except Exception as e:
                    print(f"Skipping image {xref}: extract_image failed → {e}")
                    continue

                if not extracted:
                    print(f"Empty extracted image for xref {xref}")
                    continue

                image_bytes = extracted.get("image")
                if not image_bytes:
                    print(f"No byte data for xref {xref}")
                    continue

                ext = extracted.get("ext", "png")
                img_name = f"page{page_index}_img{xref}.{ext}"
                img_path = os.path.join("processed_output/images", img_name)

                # FIX 3 → Reliable write
                try:
                    with open(img_path, "wb") as f:
                        f.write(image_bytes)
                except Exception as e:
                    print(f"Error writing {img_path}: {e}")
                    continue

                # You can also extract bbox in a separate step (optional)
                self.images.append({
                    "page": page_index,
                    "image_file": img_path,
                    "bbox": None
                })
