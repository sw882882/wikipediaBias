import warnings

import pandas as pd
from urllib.parse import urlparse
import re

from dash import Dash, html, dcc, callback, Output, Input

# import plotly.express as px
import pandas as pd

warnings.simplefilter(action="ignore", category=FutureWarning)
df = pd.read_csv("links.csv", index_col=0)


print("fixing archive links...")
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

df_frequency.to_csv("./data/output/frequency.csv")

print(df_frequency)
