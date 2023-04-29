import warnings

import pandas as pd
from urllib.parse import urlparse
import re

from dash import Dash, html, dcc, callback, Output, Input

# import plotly.express as px
import pandas as pd

warnings.simplefilter(action="ignore", category=FutureWarning)
df = pd.read_csv("./data/output/links.csv", index_col=0)


pattern = r"https://web\.archive\.org/web/\d+/(.*)"
# iterate over each column in the dataframe
for column in df.columns:
    # iterate over each row in the column
    for i in range(len(df[column])):
        # apply the regex pattern to the cell, but only if it's not null or NaN
        cell_value = df.at[i, column]
        if pd.notnull(cell_value):
            # extract the end part of the URL using the regex pattern
            match = re.search(pattern, cell_value)
            if match:
                df.at[i, column] = match.group(1)


df = df.where(pd.notnull(df), None)


# data cleaning


# define a function to extract the domain name
def extract_domain(url):
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if domain.startswith("www."):
            domain = domain[4:]  # remove the 'www.' prefix
        return domain
    except:
        return ""


# apply the function to each cell in the dataframe containing a URL
df = df.applymap(lambda x: extract_domain(x) if re.match(r"http[s]?://", str(x)) else x)

# display the result
print(df)

df_frequency = pd.DataFrame(index=df.stack().unique())

df = df.reset_index(drop=True)

print(df)

# TODO make sure to remove the random numbers before processing because there are some issues

for col in df.columns:
    # count the frequency of each unique value in the column and add it to df_frequency
    counts = df[col].value_counts()
    df_frequency[col] = df_frequency.index.map(counts.get)


df_frequency = df_frequency.drop("web.archive.org", axis=0)

df_frequency.to_csv("./data/output/frequency.csv")

print(df_frequency)
