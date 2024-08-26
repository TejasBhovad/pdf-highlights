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


@app.route('/api/generate-md')
@limiter.limit("5 per minute")  # Rate limit
def generate_md():
    pdf_path = request.args.get('pdf_path')
    if not pdf_path:
        return jsonify({"error": "PDF path is required"}), 400

    pdf_full_path = pdf_path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'static', 'highlighted_content.csv')
    md_file_path = os.path.join(base_dir, 'static', 'highlighted_content.md')

    try:
        if not os.path.exists(pdf_full_path):
            raise FileNotFoundError(f"The specified PDF file '{pdf_full_path}' was not found.")

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


@app.route('/api/generate-pdf')
@limiter.limit("5 per minute")  # Rate limit
def generate_pdf():
    pdf_path = request.args.get('pdf_path')
    if not pdf_path:
        return jsonify({"error": "PDF path is required"}), 400

    pdf_full_path = pdf_path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'static', 'highlighted_content.csv')
    pdf_file_path = os.path.join(base_dir, 'static', 'highlighted_content.pdf')

    try:
        if not os.path.exists(pdf_full_path):
            raise FileNotFoundError(f"The specified PDF file '{pdf_full_path}' was not found.")

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


@app.route('/api/get-highlighted-page')
@limiter.limit("5 per minute")  # Rate limit
def get_highlighted_page():
    pdf_path = request.args.get('pdf_path')
    if not pdf_path:
        return jsonify({"error": "PDF path is required"}), 400

    pdf_full_path = pdf_path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_file_path = os.path.join(base_dir, 'static', 'highlighted_content.pdf')

    try:
        if not os.path.exists(pdf_full_path):
            raise FileNotFoundError(f"The specified PDF file '{pdf_full_path}' was not found.")

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
