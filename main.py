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
WORD_BUFFER = 5

# Define the color definitions
color_definitions = {
    'Red': [1.0, 0.0, 0.0],
    'Yellow': [1.0, 1.0, 0.0],
    'Pink': [1.0, 0.5, 0.5],
    'Green': [0.0, 1.0, 0.0]
}

# Loop through each page
for page_index in range(len(doc)):
    page = doc[page_index]
    # Check if the page has annotations
    if page.annots():
        for annot in page.annots():
            # print(annot)
            text = page.get_text("words", clip=annot.rect)
            # print(highlighted_text)
            text = " ".join([word[4] for word in text])
            # Add the highlighted text and page number to the dictionary
            if text not in highlighted_text:
                highlighted_text[text] = [page_index + 1]
            else:
                highlighted_text[text].append(page_index + 1)


# from dict create df where all rows have same pg no and content appeneded
highlighted_text_df = pd.DataFrame(columns=["Page", "Highlighted Text"])

for text, pages in highlighted_text.items():
    new_row = pd.DataFrame({"Page": [pages], "Highlighted Text": [text]})
    highlighted_text_df = pd.concat([highlighted_text_df, new_row], ignore_index=True)

highlighted_text_df.to_csv(output_path + "highlighted_text.csv", index=False)
print(highlighted_text_df.head())