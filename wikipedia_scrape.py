import pandas as pd
from duckduckgo_search import ddg
import requests
from bs4 import BeautifulSoup
import re
from time import sleep
from datetime import datetime

# Read the data from a CSV file using pandas
df = pd.read_csv("./data/2015~.csv")

df_output = pd.DataFrame()
df_date = pd.DataFrame()

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
    dates = []
    for ref in soup.find_all("span", {"class": "reference-text"}):
        dates.append(find_earliest_date(ref.text))
        for link in ref.find_all("a"):
            href = link.get("href")
            if href and (href.startswith("http") or href.startswith("https")):
                links.append(href)
    return links, dates


# date reget (?i)\b[A-Z][a-z]{2,8} \d{1,2}, \d{4}\b
def find_earliest_date(string):
    date_pattern = r"(?i)\b[A-Z][a-z]{2,8} \d{1,2}, \d{4}\b"
    date_pattern = r"(?i)\b(?:January|Jan(?:uary)?|February|Feb(?:ruary)?|March|Mar(?:ch)?|April|Apr(?:il)?|May|June|Jun(?:e)?|July|Jul(?:y)?|August|Aug(?:ust)?|September|Sep(?:tember)?|Sept(?:ember)?|October|Oct(?:ober)?|November|Nov(?:ember)?|December|Dec(?:ember)?) \d{1,2}, \d{4}\b"

    date_strings = re.findall(date_pattern, string)
    if not date_strings:
        return None
    dates = []
    for date_string in date_strings:
        print(date_string)
        try:
            date = datetime.strptime(date_string, "%B %d, %Y")
        except:
            print("not in the format normal format")
            try:
                date = datetime.strptime(date_string, "%b %d, %Y")
            except:
                print("some other wack ass format")
        dates.append(date)
    return min(dates)


# Loop through each row in the input data frame
for index, row in df.iterrows():
    # Search for the best match for the page title
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
        sources, dates = get_source_links(best_match)
        df_output = pd.concat([df_output, pd.Series(sources, name=name)], axis=1)
        print(df_output)
        df_date = pd.concat([df_date, pd.Series(dates, name=name)], axis=1)
        print(df_date)
    else:
        df_output[name] = pd.Series(["Error with DDG"])
        print("Error with DDG")

df_output.to_csv("links.csv")
df_date.to_csv("date.csv")
