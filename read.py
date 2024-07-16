from typing import Hashable

import pandas as pd
import os

csv_path = "output/highlighted_content.csv"
#  id doesnt exist err
if not os.path.exists(csv_path):
    print("File does not exist")
    exit()

df = pd.read_csv(csv_path)
print(df.head(20))

LINE_BUFFER = 6  # Define the line buffer limit
content_clusters = []  # Initialize the list to hold clusters

index: Hashable
for index, row in df.iterrows():
    content = row["Content"]
    line_no = row["Line No"]
    page_no = row["Page"]
    if index == 0:
        # Start the first cluster
        content_clusters.append([content])
    else:
        prev_row = df.iloc[index - 1]
        prev_line_no = prev_row["Line No"]
        prev_page_no = prev_row["Page"]
        if page_no == prev_page_no:
            # Same page, check line number difference
            if line_no - prev_line_no <= LINE_BUFFER:
                content_clusters[-1].append(content)
            else:
                content_clusters.append([content])
        else:
            # New page, always start a new cluster
            content_clusters.append([content])

for cluster_index, cluster_contents in enumerate(content_clusters):
    print(f"Cluster {cluster_index + 1}:")
    for content in cluster_contents:
        print(f"    {content}")

