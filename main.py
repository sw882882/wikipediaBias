import pandas as pd
from duckduckgo_search import ddg
import requests
from bs4 import BeautifulSoup
import re
from googlesearch import search
from time import sleep

# Read the data from a CSV file using pandas
df = pd.read_csv("./data/2015~.csv")

df_output = pd.DataFrame()

# Create a new data frame to store the scraped data
results = pd.DataFrame(columns=df.columns)


def search_for_page(name):
    r = ddg(f"{name} politician site:en.wikipedia.org")
    if r is not None:
        return r[0]["href"]
    else:
        return r


def get_source_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    links = []
    for ref in soup.find_all("span", {"class": "reference-text"}):
        for link in ref.find_all("a"):
            href = link.get("href")
            if href and (href.startswith("http") or href.startswith("https")):
                links.append(href)
    return links


# Loop through each row in the input data frame
for index, row in df.iterrows():
    # Search for the best match for the page title
    # TODO edit rows here
    if str(row["middleName"]) == "nan":
        name = str(row["givenName"]) + " " + str(row["familyName"])
    else:
        name = (
            re.sub(r"[^\w\s]", "", str(row["givenName"]))
            + " "
            + re.sub(r"[^\w\s]", "", str(row["middleName"]))
            + " "
            + re.sub(r"[^\w\s]", "", str(row["familyName"]))
        )
    print(name)
    sleep(1)
    best_match = search_for_page(name)
    if best_match is not None:
        sources = get_source_links(best_match)
        df_output = pd.concat([df_output, pd.Series(sources, name=name)], axis=1)
        print(df_output)
    else:
        df_output[name] = pd.Series(["Error with DDG"])
        print("Error with DDG")

df_output.to_csv("output.csv")
