import time
import pandas as pd
from goose3 import Configuration, Goose

# Read the CSV file
df = pd.read_csv("./data/output/links.csv")

# Initialize Goose with a custom user agent
config = Configuration()
config.http_timeout = 5  # Set the timeout in seconds
config.browser_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
g = Goose(config)


def extract_data(url):
    try:
        # Extract the title, text, news source, section, and publish date using Goose3
        article = g.extract(url=url)
        title = article.title
        text = article.cleaned_text
        source = article.domain
        section = article.infos.get("section")
        publish_date = article.publish_date
        print(title)
    except Exception as e:
        print(f"Error: no workie :(")
        title = None
        text = None
        source = None
        section = None
        publish_date = None
    return title, text, source, section, publish_date


# Create new columns for the title, text, news source, section, and publish date
df["title"] = None
df["text"] = None
df["source"] = None
df["section"] = None
df["publish_date"] = None

# Iterate through the "link" column
for index, row in df.iterrows():
    url = row["links"]
    title, text, source, section, publish_date = extract_data(url)
    print(title, source, section)
    df.at[index, "title"] = title
    df.at[index, "text"] = text
    df.at[index, "source"] = source
    df.at[index, "section"] = section
    df.at[index, "publish_date"] = publish_date

    # Basic rate limiting
    time.sleep(0.3)


# Save the results to a new CSV file
df.to_csv("links_text.csv", index=False)
