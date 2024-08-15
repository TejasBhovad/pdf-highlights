import os
import pymupdf
import pandas as pd


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


def save_highlighted_text(hg_content, op_path):
    highlighted_text_list = []
    for content, details in hg_content.items():
        for page, lines in zip(details['pages'], details['lines']):
            highlighted_text_list.append({"Page": page, "Line No": lines, "Content": content})

    highlighted_text_df = pd.DataFrame(highlighted_text_list)
    highlighted_text_df.to_csv(op_path + "highlighted_content.csv", index=False)
    print(highlighted_text_df.head())
    return highlighted_text_list


def generate_clustered_content_md(csv_path: str, md_file_path: str):
    # Check if the CSV file exists
    if not os.path.exists(csv_path):
        print("File does not exist")
        return

    # Read the CSV file
    df = pd.read_csv(csv_path)
    print(df.head(20))

    # Initialize clustering variables
    LINE_BUFFER = 6  # Define the line buffer limit
    content_clusters = []  # Initialize the list to hold clusters

    # Cluster the content
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

    # Write clusters to a Markdown file
    with open(md_file_path, "w", encoding="utf-8") as md_file:
        md_file.write("# Highlighted Content\n\n")
        for cluster_index, cluster_contents in enumerate(content_clusters):
            md_file.write(f"## Cluster {cluster_index + 1}\n\n")
            for content in cluster_contents:
                wrapped_content = wrap_text(content, 80)  # Adjust line length as needed
                md_file.write(f"- {wrapped_content}\n")
            md_file.write("\n")

    print(f"MD file created: {md_file_path}")


def generate_clustered_content_pdf(csv_path: str, pdf_file_path: str):
    # Check if the CSV file exists
    if not os.path.exists(csv_path):
        print("File does not exist")
        return

    # Read the CSV file
    df = pd.read_csv(csv_path)
    print(df.head(20))

    # Initialize clustering variables
    LINE_BUFFER = 6  # Define the line buffer limit
    content_clusters = []  # Initialize the list to hold clusters

    # Cluster the content
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

    # Create a PDF document
    pdf_document = pymupdf.open()
    page = pdf_document.new_page()

    # Constants for positioning and font sizes
    LEFT_MARGIN = 72
    TOP_MARGIN = 72
    BOTTOM_MARGIN = 72
    PAGE_WIDTH, PAGE_HEIGHT = page.rect.width, page.rect.height
    LINE_SPACING = 14  # Spacing between lines of text
    CLUSTER_SPACING = 20  # Spacing between clusters
    TITLE_FONT_SIZE = 16
    CONTENT_FONT_SIZE = 11

    def calculate_text_height(text, fontsize, line_spacing):
        """Calculate the height of the text block."""
        line_count = text.count("\n") + 1
        return line_count * (fontsize + line_spacing)

    # Write clusters to the PDF
    y_position = TOP_MARGIN  # Initial y position
    for cluster_index, cluster_contents in enumerate(content_clusters):
        # Insert cluster title
        cluster_title = f"## Cluster {cluster_index + 1}"
        title_height = calculate_text_height(cluster_title, TITLE_FONT_SIZE, LINE_SPACING)
        content_text = ""
        for content in cluster_contents:
            wrapped_content = wrap_text(content, 80)  # Adjust line length as needed
            content_text += f"- {wrapped_content}\n"

        content_height = calculate_text_height(content_text, CONTENT_FONT_SIZE, LINE_SPACING)

        # Check if there is enough space on the current page, else create a new page
        total_cluster_height = title_height + content_height + CLUSTER_SPACING
        if y_position + total_cluster_height > PAGE_HEIGHT - BOTTOM_MARGIN:
            page = pdf_document.new_page()
            y_position = TOP_MARGIN  # Reset y position for new page

        # Insert title
        rc = page.insert_text((LEFT_MARGIN, y_position), cluster_title, fontname="helv", fontsize=TITLE_FONT_SIZE)
        y_position += title_height

        # Insert cluster contents
        rc = page.insert_text((LEFT_MARGIN, y_position), content_text, fontname="helv", fontsize=CONTENT_FONT_SIZE)
        y_position += content_height + CLUSTER_SPACING  # Add space after the cluster

    pdf_document.save(pdf_file_path)
    pdf_document.close()

    print(f"PDF file created: {pdf_file_path}")
