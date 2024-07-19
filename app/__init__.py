import os
from flask import Flask, url_for
from app.utils.file import generate_clustered_content_md

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World'


@app.route('/generate-md')
def generate_md():
    # Construct the file paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'static', 'highlighted_content.csv')
    md_file_path = os.path.join(base_dir, 'static', 'highlighted_content.md')

    try:
        generate_clustered_content_md(csv_path, md_file_path)
    except Exception as e:
        return str(e)
    return f"MD file created: {md_file_path}"


if __name__ == '__main__':
    app.run(debug=True)