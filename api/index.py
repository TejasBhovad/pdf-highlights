import logging
from io import BytesIO

import pymupdf
import requests
from flask import Flask, send_file
from flask import jsonify, request
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

    try:
        # Load PDF from S3 URL
        response = requests.get(pdf_path)
        if response.status_code != 200:
            raise Exception(f"Failed to load PDF from {pdf_path}. Status code: {response.status_code}")

        pdf_file = BytesIO(response.content)

        # Open the PDF document
        doc = pymupdf.open(stream=pdf_file, filetype="pdf")
        highlighted_text = extract_highlighted_text_with_line_numbers(doc)

        # Save highlighted text to CSV in memory
        csv_data = save_highlighted_csv(highlighted_text)

        # Generate Markdown content in memory
        md_output = generate_clustered_content_md(csv_data)
        # print md in string format
        md_file_content = md_output.getvalue().decode('utf-8')
        print("Markdown content created in memory")
        # Return the Markdown as a response
        return send_file(md_output, as_attachment=True, download_name='highlighted_content.md',
                         mimetype='text/markdown')

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred."}), 500


@app.route('/api/generate-pdf')
@limiter.limit("5 per minute")  # Rate limit
def generate_pdf():
    pdf_path = request.args.get('pdf_path')
    if not pdf_path:
        return jsonify({"error": "PDF path is required"}), 400

    try:
        # Load PDF from S3 URL
        response = requests.get(pdf_path)
        if response.status_code != 200:
            raise Exception(f"Failed to load PDF from {pdf_path}. Status code: {response.status_code}")

        pdf_file = BytesIO(response.content)

        # Open the PDF document
        doc = pymupdf.open(stream=pdf_file, filetype="pdf")
        highlighted_text = extract_highlighted_text_with_line_numbers(doc)

        # Create a BytesIO object for the output PDF
        output_pdf = BytesIO()

        # Save highlighted text to a CSV in memory
        csv_data = save_highlighted_csv(highlighted_text)

        # Generate the clustered content PDF in memory
        generate_clustered_content_pdf(csv_data, output_pdf)

        # Move the cursor of the BytesIO object to the beginning
        output_pdf.seek(0)

        # Return the PDF as a response
        return send_file(output_pdf, as_attachment=True, download_name='highlighted_content.pdf',
                         mimetype='application/pdf')

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred."}), 500


@app.route('/api/get-highlighted-page')
@limiter.limit("5 per minute")  # Rate limit
def get_highlighted_page():
    pdf_path = request.args.get('pdf_path')
    if not pdf_path:
        return jsonify({"error": "PDF path is required"}), 400

    try:
        # Load PDF from S3 URL
        response = requests.get(pdf_path)
        if response.status_code != 200:
            raise Exception(f"Failed to load PDF from {pdf_path}. Status code: {response.status_code}")

        pdf_file = BytesIO(response.content)

        # Open the PDF document
        doc = pymupdf.open(stream=pdf_file, filetype="pdf")

        pages_list = get_highlighted_pages(doc)
        if not pages_list:
            return jsonify({"error": "No highlighted pages found."}), 404

        # Create a BytesIO object for the output PDF
        output_pdf = BytesIO()

        # Extract highlighted text and create a new PDF in memory
        extract_highlighted_text_with_line_numbers_on_pages(doc, pages_list, output_pdf)

        # Move the cursor of the BytesIO object to the beginning
        output_pdf.seek(0)

        # Return the PDF as a response
        return send_file(output_pdf, as_attachment=True, download_name='highlighted_content.pdf',
                         mimetype='application/pdf')

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred."}), 500


@app.route('/api/')
def hello_world():
    return 'Hello, World'


if __name__ == '__main__':
    app.run(debug=True)
