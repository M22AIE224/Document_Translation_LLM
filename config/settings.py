import os

# Load OpenAI Key
with open("data/api_key.txt") as f:
    os.environ["OPENAI_API_KEY"] = f.read().strip()

OPENAI_MODEL = "gpt-4o-mini"
TARGET_LANG = "hi"
SOURCE_LANG = "en"
