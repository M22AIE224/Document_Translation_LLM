from openai import OpenAI
import os

MODEL_NAME = "gpt-4o-mini"

with open('data/api_key.txt') as f:
    os.environ["OPENAI_API_KEY"] = f.read().strip()


class Translator:

    def __init__(self):
        self.client = OpenAI()

    def translate_text(self, text, target_lang="hi"):
        if not text.strip():
            return ""

        prompt = f"""
Translate the following text into {target_lang}.
Maintain the original formatting and structure.

Text:
{text}
        """

        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content.strip()

    def translate_blocks(self, blocks, target_lang="hi"):
        translated_blocks = []
        for block in blocks:
            page = block["page"]
            text = block["text"]
            translated_text = self.translate_text(text, target_lang)
            translated_blocks.append({
                "page": page,
                "bbox": block["bbox"],
                "text": translated_text
            })
        return translated_blocks
