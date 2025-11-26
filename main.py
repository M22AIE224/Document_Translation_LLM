import os
from agents.block_extractor import PDFBlockExtractor
#from agents.extractor_old import PDFExtractor
from agents.block_translator import BlockTranslator
#from agents.pdf_rebuilder import PDFRebuilder
from agents.pdf_rebuilder import PDFRebuilder
from agents.hindi_mapper import map_hindi_to_blocks   # only if you use mapping


def process_pdf(input_pdf, output_pdf):

    print("\n🔍 STEP 1 — Extracting PDF blocks/images/tables...")
    extractor = PDFBlockExtractor(input_pdf)
    data = extractor.extract()

    original_blocks = data["blocks"]
    images = data["images"]
    tables = data["tables"]
    page_sizes = data["page_sizes"]

    print(f"Total blocks extracted: {len(original_blocks)}")

    # -------------------------------------------------------
    # 🔥 STEP 2 — Translate English → Hindi
    # -------------------------------------------------------
    print("\n🌐 STEP 2 — Translating Text blocks to Hindi...")
    translator = BlockTranslator()
    translated_blocks = translator.translate_blocks(original_blocks, target_lang="hi")

   

    print(f"Translated blocks: {len(translated_blocks)}")

    # -------------------------------------------------------
    # OPTIONAL: Hindi mapping (only if needed)
    # -------------------------------------------------------
    # mapped_blocks = map_hindi_to_blocks(translated_blocks)

    final_blocks = translated_blocks  # ensure ONLY Hindi goes forward

    # Debug: Print first few final blocks
    print("\n=== SAMPLE OF FINAL HINDI BLOCKS SENT TO REBUILDER ===")
    for b in final_blocks[:3]:
        print(f"[PAGE {b['page']}] {b['text'][:100]}...")


    print("\n🌐 STEP 3 — Translating Tabular Text to Hindi...")
    translated_tables = []
    for tbl in tables:
        t = tbl.copy()
        t["data"] = translator.translate_table(tbl["data"], target_lang="hi")
        translated_tables.append(t)

    # -------------------------------------------------------
    # 🧱 STEP 3 — Rebuild clean Hindi PDF
    # -------------------------------------------------------
    print("\n🌐STEP 4 — Rebuilding Hindi PDF...")
    rebuilder = PDFRebuilder(page_sizes)

    rebuilder.rebuild(
        output_path=output_pdf,
        blocks=final_blocks,  # ONLY HINDI BLOCKS!
        images=images,
        tables=translated_tables,
    )

    print("\n🎉 PDF processing completed successfully!")
    print(f"Output saved at: {output_pdf}")


# Manual run test
if __name__ == "__main__":
    input_path = "input.pdf"
    output_path = "output_hindi.pdf"
    process_pdf(input_path, output_path)
