import pandas as pd
import re

# Load the CSV file into a pandas DataFrame
df = pd.read_csv("output.csv")

# Define a regular expression to match the archived URLs
pattern = r"https://web\.archive\.org/web/\d+/(.*)"

# Iterate over each cell in the DataFrame and replace archived URLs with unarchived URLs
for column in df.columns:
    for index, cell in df[column].iteritems():
        urls = re.findall(pattern, str(cell))
        if urls:
            for url in urls:
                unarchived_url = url
            df.at[index, column] = unarchived_url

# Save the updated DataFrame to a new CSV file
df.to_csv("unarchived_links.csv", index=False)
