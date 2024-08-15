# PDF Annotation Extractor

Extract highlighted text from a PDF file and save to a CSV file.

## Description

Many people use PDF files to read and highlight important text as they read. It can be painful to go back and refer to the highlighted text. This application helps to extract the highlighted text from a PDF file and save it to a CSV file. And later on, users will be able to download a markdown flavored PDF file with the extracted annotations. 

## Usage

> Its recommended to use a virtual environment to run the application like conda or venv.

```bash
pip install -r requirements.txt
```

```bash
python main.py
```

Testing 
```bash
http://127.0.0.1:5000/generate-md?pdf_path=sample.pdf
```

## Todo
- [x] Extract highlighted text from a PDF file.
- [x] Save the extracted text to a CSV file.
- [x] Create a markdown flavored PDF file for download.
- [x] Add a flask EndPoint to upload a PDF file and return the extracted annotations.
- [ ] organize the code using classes.
- [ ] Add a GUI for the application(using Svelte/astro)
- [ ] Add feature to only show pages which have annotations.

## References
https://pymupdf.readthedocs.io/en/latest/recipes-annotations.html#annotations