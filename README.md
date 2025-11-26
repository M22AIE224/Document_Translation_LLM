# =============== Overview  ================
PDF Multilingual Translation Pipeline

High-Fidelity PDF Translation With Layout Preservation

This project converts PDF documents into another language (e.g., English → Hindi) while preserving the original layout, including:

Multi-column pages

Tables & internal cell structure

Images

Exact block positions

Fonts (Unicode + Devanagari support)

The system includes a full end-to-end pipeline:

User Interface → Main Controller → Block Extractor → Block Translator → PDF Rebuilder


# =========== Project Structure  ==========
pdf_translator/
│
├── main.py                       # Orchestrates the pipeline
├── user_interface/
│   └── app.py                    # Flask UI
│
├── agents/
│   ├── block_extractor.py        # Extracts text blocks, tables, images
│   ├── block_translator.py       # Translates text blocks
│   ├── hindi_mapper.py           # Optional language helper
│   ├── translator.py             # Block-level translation orchestrator
│   ├── rebuilder.py              # Rebuilds translated PDF with layout
│   └── __init__.py
│
├── font/
│   ├── NotoSansDevanagari-Regular.ttf
│   └── NotoSansDevanagari-VariableFont.ttf
│
├── data/
│   └── api_key.txt               # OpenAI key
│
└── static/
    └── uploaded/ 



# ===System Architecture (Layer Overview)====

1. User Interface (Flask App)

Accepts PDF upload

Sends to main.process_pdf()

Returns final translated PDF

2. Main Controller

Coordinates the pipeline:

extract → translate → rebuild → output

3. Block Extractor

Uses PDFPlumber

Detects:

Page-level text

Multi-column flows

Tables with cell boundaries

Images + bounding boxes

Removes nested table-text from outer blocks

Outputs clean structured blocks

4. Block Translator

Uses OpenAI GPT-4o / GPT-4o-mini

Translates with formatting constraints

Handles:

Line breaks

Page-wise mapping

Table cell-wise translation

5. PDF Rebuilder

Uses ReportLab

Preserves:

Original widths

Original heights

Exact bounding boxes

Table structure

Uses Noto Sans Devanagari for Hindi

Produces final PDF identical to original layout

# ====== Installation & Setup ===========

1. Clone the repo
git clone https://github.com/M22AIE224/Document_Translation_LLM.git
cd Document_Translation_LLM

2. Install dependencies
pip install -r requirements.txt

3. Add OpenAI API Key

Create:

data/api_key.txt


Add your key inside.

4. Install fonts (already included)

If needed, download from Google Fonts:

Noto Sans Devanagari

Place inside /font/.

# ======== Running the App ==============
Run UI
python user_interface/app.py


Open:

http://127.0.0.1:5000

