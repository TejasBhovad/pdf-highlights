from io import BytesIO

import pandas as pd
import pymupdf


def extract_highlighted_text_with_line_numbers(doc_file):
    highlighted_text_with_lines = {}
    for page_index in range(len(doc_file)):
        page = doc_file[page_index]
        text_blocks = page.get_text("blocks")
        if page.annots():
            for annot in page.annots():
                annot_rect = annot.rect
                annot_center = [(annot_rect[0] + annot_rect[2]) / 2, (annot_rect[1] + annot_rect[3]) / 2]
                text = page.get_text("words", clip=annot_rect)
                content = " ".join([word[4] for word in text])
                line_numbers = [i + 1 for i, block in enumerate(text_blocks) if
                                block[0] <= annot_center[0] <= block[2] and block[1] <= annot_center[1] <= block[3]]
                if content not in highlighted_text_with_lines:
                    highlighted_text_with_lines[content] = {'pages': [page_index + 1], 'lines': line_numbers}
                else:
                    highlighted_text_with_lines[content]['pages'].append(page_index + 1)
                    for line_number in line_numbers:
                        if line_number not in highlighted_text_with_lines[content]['lines']:
                            highlighted_text_with_lines[content]['lines'].extend(line_numbers)
    return highlighted_text_with_lines


def generate_clustered_content_md(csv_data):
    if not csv_data:
        print("No data to generate Markdown")
        return BytesIO()  # Return an empty BytesIO object

    df = pd.DataFrame(csv_data)

    LINE_BUFFER = 6
    content_clusters = []

    for index, row in df.iterrows():
        content = row["Content"]
        line_no = row["Line No"]
        page_no = row["Page"]
        if index == 0:
            content_clusters.append([content])
        else:
            prev_row = df.iloc[index - 1]
            prev_line_no = prev_row["Line No"]
            prev_page_no = prev_row["Page"]
            if page_no == prev_page_no:
                if line_no - prev_line_no <= LINE_BUFFER:
                    content_clusters[-1].append(content)
                else:
                    content_clusters.append([content])
            else:
                content_clusters.append([content])

    def wrap_text(text, line_length):
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + len(current_line) > line_length:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += len(word)

        if current_line:
            lines.append(" ".join(current_line))

        return "\n".join(lines)

    # Create a BytesIO object for the Markdown content
    md_output = BytesIO()
    md_output.write(b"# Highlighted Content\n\n")

    for cluster_index, cluster_contents in enumerate(content_clusters):
        for content in cluster_contents:
            wrapped_content = wrap_text(content, 80)
            md_output.write(f"- {wrapped_content}\n".encode('utf-8'))
        md_output.write(b"\n")

    # Move the cursor of the BytesIO object to the beginning
    md_output.seek(0)
    return md_output

def generate_clustered_content_pdf(csv_data, output_pdf):
    if not csv_data:
        print("No data to generate PDF")
        return

    df = pd.DataFrame(csv_data)

    LINE_BUFFER = 6
    content_clusters = []

    for index, row in df.iterrows():
        content = row["Content"]
        line_no = row["Line No"]
        page_no = row["Page"]
        if index == 0:
            content_clusters.append([content])
        else:
            prev_row = df.iloc[index - 1]
            prev_line_no = prev_row["Line No"]
            prev_page_no = prev_row["Page"]
            if page_no == prev_page_no:
                if line_no - prev_line_no <= LINE_BUFFER:
                    content_clusters[-1].append(content)
                else:
                    content_clusters.append([content])
            else:
                content_clusters.append([content])

    def wrap_text(text, line_length):
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + len(current_line) > line_length:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += len(word)

        if current_line:
            lines.append(" ".join(current_line))

        return "\n".join(lines)

    pdf_document = pymupdf.open()
    page = pdf_document.new_page()

    LEFT_MARGIN = 72
    TOP_MARGIN = 72
    BOTTOM_MARGIN = 72
    PAGE_WIDTH, PAGE_HEIGHT = page.rect.width, page.rect.height
    LINE_SPACING = 14
    CLUSTER_SPACING = 20
    TITLE_FONT_SIZE = 16
    CONTENT_FONT_SIZE = 11

    def calculate_text_height(text, fontsize, line_spacing):
        line_count = text.count("\n") + 1
        return line_count * (fontsize + line_spacing)

    y_position = TOP_MARGIN
    for cluster_index, cluster_contents in enumerate(content_clusters):
        cluster_title = f"## Cluster {cluster_index + 1}"
        title_height = calculate_text_height(cluster_title, TITLE_FONT_SIZE, LINE_SPACING)
        content_text = ""
        for content in cluster_contents:
            wrapped_content = wrap_text(content, 80)
            content_text += f"- {wrapped_content}\n"

        content_height = calculate_text_height(content_text, CONTENT_FONT_SIZE, LINE_SPACING)

        total_cluster_height = title_height + content_height + CLUSTER_SPACING
        if y_position + total_cluster_height > PAGE_HEIGHT - BOTTOM_MARGIN:
            page = pdf_document.new_page()
            y_position = TOP_MARGIN

        page.insert_text((LEFT_MARGIN, y_position), cluster_title, fontname="helv", fontsize=TITLE_FONT_SIZE)
        y_position += title_height

        page.insert_text((LEFT_MARGIN, y_position), content_text, fontname="helv", fontsize=CONTENT_FONT_SIZE)
        y_position += content_height + CLUSTER_SPACING

    pdf_document.save(output_pdf)
    pdf_document.close()

    print("PDF file created in memory")


def save_highlighted_csv(hg_content):
    highlighted_text_list = []
    for content, details in hg_content.items():
        for page, lines in zip(details['pages'], details['lines']):
            highlighted_text_list.append({"Page": page, "Line No": lines, "Content": content})

    return highlighted_text_list


def get_highlighted_pages(doc_file):
    highlighted_pages = []
    for page_index in range(len(doc_file)):
        page = doc_file[page_index]
        if page.annots():
            for annot in page.annots():
                if annot.type[0] == 8:
                    highlighted_pages.append(page_index + 1)
                    break
    return highlighted_pages


def extract_highlighted_text_with_line_numbers_on_pages(doc_file, pages_list, output_pdf_path):
    new_pdf = pymupdf.open()

    for page_index in pages_list:
        new_pdf.insert_pdf(doc_file, from_page=page_index - 1, to_page=page_index - 1)

    new_pdf.save(output_pdf_path)
    new_pdf.close()

    print(f"New PDF file created: {output_pdf_path}")
