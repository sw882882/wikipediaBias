import pandas as pd
from duckduckgo_search import ddg
import requests
from bs4 import BeautifulSoup
import re
from time import sleep
from datetime import datetime
from difflib import SequenceMatcher
import urllib.parse

# Read the data from a CSV file using pandas
df = pd.read_csv("./data/source/2015~.csv")
df_allsides = pd.read_csv("./data/output/allsides.csv")


def clean_urls(links):
    new_links = []
    for link in links:
        http_count = link.count("http")
        if http_count > 1:
            idx = link.find("http", link.find("http") + 1)
            new_links.append(link[idx:])
        else:
            new_links.append(link)
    return new_links


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
        for link in ref.find_all("a"):
            href = link.get("href")
            if href and (href.startswith("http") or href.startswith("https")):
                links.append(href)
                date = find_earliest_date(ref.text)
                if date is not None:
                    dates.append(date)
                else:
                    dates.append(None)
    return links, dates


# date reget (?i)\b[A-Z][a-z]{2,8} \d{1,2}, \d{4}\b
def find_earliest_date(string):
    date_pattern = r"(?i)\b(?:January|Jan(?:uary)?|February|Feb(?:ruary)?|March|Mar(?:ch)?|April|Apr(?:il)?|May|June|Jun(?:e)?|July|Jul(?:y)?|August|Aug(?:ust)?|September|Sep(?:tember)?|Sept(?:ember)?|October|Oct(?:ober)?|November|Nov(?:ember)?|December|Dec(?:ember)?) \d{1,2}, \d{4}\b"

    date_strings = re.findall(date_pattern, string)
    if not date_strings:
        return None
    dates = []
    for date_string in date_strings:
        date = None
        try:
            date = datetime.strptime(date_string, "%B %d, %Y")
        except:
            try:
                date = datetime.strptime(date_string, "%b %d, %Y")
            except:
                print("some other wack ass format")
                return None
        dates.append(date)

    return min(dates)


def get_bias(url):
    # Parse the root domain from the input URL
    try:
        root_domain = (
            urllib.parse.urlparse(url).hostname.split(".")[-2]
            + "."
            + urllib.parse.urlparse(url).hostname.split(".")[-1]
        )
    except:
        return None, "Other"
    # Find rows with matching root domains
    matching_rows = df_allsides[
        df_allsides["source_link"].str.contains(root_domain, na=False)
    ]

    # Initialize variables for the highest similarity score and corresponding row
    highest_score = 0
    best_row = None

    # Iterate over the matching rows and find the one with the highest similarity score
    for index, row in matching_rows.iterrows():
        similarity_score = SequenceMatcher(None, url, row["source_link"]).ratio()
        if similarity_score > highest_score:
            highest_score = similarity_score
            best_row = row

    # If no matching row was found, return None for both values
    if best_row is None:
        return None, "Other"

    # Otherwise, return the bias and text for the best matching row
    print(best_row["text"])
    return best_row["bias"], best_row["text"]


final_dates = []
final_names = []
final_links = []
final_bias = []
final_source_name = []
wikipedia_links = []
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
    sleep(0.5)
    best_match = search_for_page(name)
    if best_match is not None:
        sources, dates = get_source_links(best_match)
        wikipedia_links.extend([best_match] * len(sources))
        print(len(sources), len(dates))
        names = [name] * len(sources)
        if len(names) == len(sources) == len(dates):
            print("looks like its going good")
            final_names.extend(names)
            final_dates.extend(dates)
            final_links.extend(sources)
            # break  # FOR FUTURE ME TEMP
        else:
            print(":( failed")
            print(len(sources), len(dates))
    else:
        print("Error with DDG")
# TODO not working fix this
final_links = clean_urls(final_links)

for link in final_links:
    bias, name = get_bias(link)
    final_bias.append(bias)
    final_source_name.append(name)
    print(bias, name)

df_output = pd.DataFrame(
    list(
        zip(
            final_names,
            final_dates,
            final_links,
            final_source_name,
            final_bias,
            wikipedia_links,
        )
    ),
    columns=["name", "date", "links", "source name", "bias", "wikipedia link"],
)

print(df_output)
df_output.to_csv("links.csv")
