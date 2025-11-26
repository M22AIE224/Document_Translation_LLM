def map_hindi_to_blocks(original_blocks, translated_blocks):
    page_to_translated = {b["page"]: b["text"] for b in translated_blocks}
    mapped_blocks = []

    for block in original_blocks:
        page = block["page"]
        hindi_text = page_to_translated.get(page, "")

        mapped_blocks.append({
            "page": page,
            "bbox": block["bbox"],
            "text": hindi_text
        })

    return mapped_blocks
