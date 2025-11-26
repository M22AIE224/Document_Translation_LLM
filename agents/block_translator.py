from openai import OpenAI
import os

# Load API key
with open("data/api_key.txt") as f:
    os.environ["OPENAI_API_KEY"] = f.read().strip()

MODEL_NAME = "gpt-4o-mini"


class BlockTranslator:

    def __init__(self):
        self.client = OpenAI()

    def translate_block(self, text, target_lang="hi"):
        text = text.strip()
        if not text:
            return ""

        # The CRITICAL FIX: preserve newlines explicitly
        prompt = f"""
You are a precise translation engine.

Translate the text below into **{target_lang}**.

### RULES
- Keep line breaks exactly the same.
- Keep spacing identical.
- Do NOT merge lines.
- Do NOT remove lines.
- Do NOT reorder lines.
- Translate **every line** even if small.
- If a line is empty, return an empty line.

### TEXT TO TRANSLATE:
{text}

### OUTPUT:
(Return translation ONLY, no explanations)
"""

        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content.strip()

    def translate_blocks(self, blocks, target_lang="hi"):
        translated = []
        
        for block in blocks:
            translated_text = self.translate_block(block["text"], target_lang)

            # Make a COPY of block so original extraction is preserved
            new_block = block.copy()

            # Replace English with Hindi
            new_block["text"] = translated_text

            translated.append(new_block)

        return translated


    def translate_table(self, table_data, target_lang="hi"):
        translated_rows = []

        for row in table_data:
            translated_row = []
            for cell in row:
                if cell and isinstance(cell, str):
                    translated_cell = self.translate_block(cell, target_lang)
                else:
                    translated_cell = cell
                translated_row.append(translated_cell)

            translated_rows.append(translated_row)

        return translated_rows