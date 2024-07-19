from flask import Flask, request
import os
import pymupdf
from app.utils.file import generate_clustered_content_md, extract_highlighted_text_with_line_numbers, \
    save_highlighted_text

app = Flask(__name__)


@app.route('/generate-md')
def generate_md():
    # Retrieve the PDF file path from query parameters
    pdf_path = request.args.get('pdf_path')
    if not pdf_path:
        return "PDF path is required", 400

    # Directly use the pdf_path as it's expected to be an absolute path
    pdf_full_path = pdf_path

    # Define paths for CSV and MD files relative to the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'static', 'highlighted_content.csv')
    md_file_path = os.path.join(base_dir, 'static', 'highlighted_content.md')

    # Extract highlighted text from PDF and save to CSV
    try:
        doc = pymupdf.open(pdf_full_path)
        highlighted_text = extract_highlighted_text_with_line_numbers(doc)
        save_highlighted_text(highlighted_text, os.path.join(base_dir, 'static/'))

        # Generate Markdown from CSV
        generate_clustered_content_md(csv_path, md_file_path)
    except Exception as e:
        return str(e)

    return f"MD file created: {md_file_path}"


@app.route('/')
def hello_world():
    return 'Hello, World'


if __name__ == '__main__':
    app.run(debug=True)
