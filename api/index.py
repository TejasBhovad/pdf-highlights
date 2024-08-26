from flask import Flask, request, url_for, jsonify
import os
import pymupdf
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from api.utils.file import (
    generate_clustered_content_md,
    extract_highlighted_text_with_line_numbers,
    save_highlighted_csv,
    generate_clustered_content_pdf,
    get_highlighted_pages,
    extract_highlighted_text_with_line_numbers_on_pages
)
import logging

app = Flask(__name__)
limiter = Limiter(key_func=get_remote_address)

# Set up logging
logging.basicConfig(level=logging.ERROR)

# Create an uploads directory if it doesn't exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/api/generate-md', methods=['POST'])
@limiter.limit("5 per minute")  # Rate limit
def generate_md():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded file to the uploads directory
    pdf_full_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_full_path)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'static', 'highlighted_content.csv')
    md_file_path = os.path.join(base_dir, 'static', 'highlighted_content.md')

    try:
        doc = pymupdf.open(pdf_full_path)
        highlighted_text = extract_highlighted_text_with_line_numbers(doc)
        save_highlighted_csv(highlighted_text, os.path.join(base_dir, 'static/'))
        generate_clustered_content_md(csv_path, md_file_path)
    except FileNotFoundError as e:
        logging.error(f"FileNotFoundError: {str(e)}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred."}), 500

    return jsonify({"url": url_for('static', filename='highlighted_content.md', _external=True)})


@app.route('/api/generate-pdf', methods=['POST'])
@limiter.limit("5 per minute")  # Rate limit
def generate_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded file to the uploads directory
    pdf_full_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_full_path)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'static', 'highlighted_content.csv')
    pdf_file_path = os.path.join(base_dir, 'static', 'highlighted_content.pdf')

    try:
        doc = pymupdf.open(pdf_full_path)
        highlighted_text = extract_highlighted_text_with_line_numbers(doc)
        save_highlighted_csv(highlighted_text, os.path.join(base_dir, 'static/'))
        generate_clustered_content_pdf(csv_path, pdf_file_path)
    except FileNotFoundError as e:
        logging.error(f"FileNotFoundError: {str(e)}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred."}), 500

    return jsonify({"url": url_for('static', filename='highlighted_content.pdf', _external=True)})


@app.route('/api/get-highlighted-page', methods=['POST'])
@limiter.limit("5 per minute")  # Rate limit
def get_highlighted_page():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded file to the uploads directory
    pdf_full_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_full_path)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_file_path = os.path.join(base_dir, 'static', 'highlighted_content.pdf')

    try:
        doc = pymupdf.open(pdf_full_path)
        pages_list = get_highlighted_pages(doc)
        if not pages_list:
            return jsonify({"error": "No highlighted pages found."}), 404
        extract_highlighted_text_with_line_numbers_on_pages(doc, pages_list, pdf_file_path)
    except FileNotFoundError as e:
        logging.error(f"FileNotFoundError: {str(e)}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred."}), 500

    return jsonify({"url": url_for('static', filename='highlighted_content.pdf', _external=True)})


@app.route('/api/')
def hello_world():
    return 'Hello, World'


if __name__ == '__main__':
    app.run(debug=True)
