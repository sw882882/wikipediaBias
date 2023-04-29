import pandas as pd
from duckduckgo_search import ddg
import requests
from bs4 import BeautifulSoup
import re
from time import sleep
from datetime import datetime
from fuzzywuzzy import process
from urllib.parse import urlparse

# Read the data from a CSV file using pandas
df = pd.read_csv("./data/source/2015~.csv")
df_allsides = pd.read_csv("./data/output/allsides.csv")


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


# TODO fix its broken, limit url size or just hard code it
# so probably take the opposite approach, match url then from the matching urls do the similarity stuff
def get_bias(query_string):
    # Find the best matching string in the source_link column
    best_match = process.extractOne(query_string, df_allsides["source_link"])[0]

    # Check if the best match has the same root domain as the query string
    try:
        query_root = urlparse(query_string).hostname
        match_root = urlparse(best_match).hostname
        if query_root != match_root:
            print("websites not matching", query_root, query_string)
            return None, "other"
        # Get the bias and text data from the matching row
        row = df_allsides[df_allsides["source_link"] == best_match].iloc[0]
        return row["bias"], row["text"]
    except:
        print("BIG ERROR BIG ERROR")
        print(query_string)
        print(best_match)
        return None, "other"


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

pattern = r"^https://web\.archive\.org/web/\d{14}/(http|https)://(.*)$"
pattern = r"^https://archive\.today/\d{14}/(http|https)://(.*)$"

for i in range(len(final_links)):
    match = re.match(pattern, final_links[i])
    match_today = re.match(pattern, final_links[i])
    if match:
        final_links[i] = match.group(1) + "://" + match.group(2)
    if match_today:
        final_links[i] = match_today.group(1) + "://" + match.group(2)

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
