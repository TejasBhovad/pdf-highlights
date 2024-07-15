import pymupdf
import pandas as pd
import os

input_path = "assets/book-test.pdf"
#  id doesnt exist err
if not os.path.exists(input_path):
    print("File does not exist")
    exit()
doc = pymupdf.open(input_path)

output_path = "output/"

highlighted_text = {}


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
    highlighted_text_df.to_csv(op_path + "hg_content.csv", index=False)
    print(highlighted_text_df.head())
    return highlighted_text_list


if __name__ == "__main__":
    highlighted_text = extract_highlighted_text_with_line_numbers(doc)
    print(highlighted_text)
    save_highlighted_text(highlighted_text, output_path)
