import os

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

    # Write clusters to a Markdown file
    with open(md_file_path, "w", encoding="utf-8") as md_file:
        md_file.write("# Highlighted Content\n\n")
        for cluster_index, cluster_contents in enumerate(content_clusters):
            md_file.write(f"## Cluster {cluster_index + 1}\n\n")
            for content in cluster_contents:
                md_file.write(f"- {content}\n")
            md_file.write("\n")

    print(f"MD file created: {md_file_path}")
