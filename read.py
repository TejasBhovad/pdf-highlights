from typing import Hashable
import pandas as pd
import os


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


csv_path = "output/highlighted_content.csv"
md_file_path = "output/highlighted_content.md"
generate_clustered_content_md(csv_path, md_file_path)
