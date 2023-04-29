import pandas as pd
import requests
from bs4 import BeautifulSoup
from time import sleep

complete = False


def scrape_table_data(html):
    global complete
    soup = BeautifulSoup(html, "html.parser")
    tr_classes = ["odd views-row-first", "even", "odd", "even views-row-last"]
    td_class = "views-field views-field-title source-title"
    data = []
    for tr_class in tr_classes:
        rows = soup.find_all("tr", {"class": tr_class})
        for row in rows:
            td = row.find("td", {"class": td_class})
            a = td.find("a")
            if a:
                text = a.text.strip()
                link = a["href"]
                data.append({"text": text, "link": link})
    return data


data = []

for page_number in range(22):
    url = f"https://www.allsides.com/media-bias/ratings?page={page_number}&field_featured_bias_rating_value=All&field_news_source_type_tid[0]=2&field_news_source_type_tid[1]=3&field_news_source_type_tid[2]=4&field_news_source_type_tid[3]=5&field_news_bias_nid_1[1]=1&field_news_bias_nid_1[2]=2&field_news_bias_nid_1[3]=3&title="
    response = requests.get(url)
    data.append(scrape_table_data(response.text))
    sleep(0.5)
    print("getting the pages...")

data = [item for sublist in data for item in sublist]

df = pd.DataFrame(data)

df["link"] = "https://www.allsides.com" + df["link"].astype(str)

# Create empty lists to store the new data
bias = []
source_link = []

# Loop through the links in the dataframe
for link in df["link"]:
    # Use requests to get the HTML content of the page
    page = requests.get(link)

    # Use Beautiful Soup to parse the HTML content
    soup = BeautifulSoup(page.content, "html.parser")

    # Find the div with class "numerical-bias-rating"
    bias_div = soup.find("div", class_="numerical-bias-rating")

    # If the div exists, append the text to the bias list
    if bias_div:
        bias.append(bias_div.text.strip())
    else:
        bias.append(None)

    # Find all the links with class "external-link"
    source_links = soup.find_all("a", class_="external-link")

    # If any links exist, append the first one to the source_link list
    if source_links:
        source_link.append(source_links[0]["href"])
    else:
        source_link.append(None)
    sleep(0.5)
    print("bias rating...")

# Add the new columns to the dataframe
df["bias"] = bias
df["source_link"] = source_link

print(df)

df.to_csv("allsides.csv")
