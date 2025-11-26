from flask import Flask, render_template, request, send_file
import os
import uuid

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import process_pdf

app = Flask(__name__, template_folder="templates")

UPLOAD_FOLDER = "user_interface/uploads"
OUTPUT_FOLDER = "output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("pdf_file")
        if not file or file.filename == "":
            return render_template("index.html", error="No file selected.")

        file_id = uuid.uuid4().hex
        input_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.pdf")
        output_path = os.path.join(OUTPUT_FOLDER, f"{file_id}_translated.pdf")

        file.save(input_path)
        process_pdf(input_path, output_path)
        
        return render_template("index.html", download_link=f"/download/{file_id}_translated.pdf")

    return render_template("index.html")

@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=5000)