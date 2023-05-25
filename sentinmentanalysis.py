from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
import numpy as np
from scipy.special import softmax
import pandas as pd

df = pd.read_csv("./data/output/links_text.csv")
df = df.replace({np.nan: None})

MODEL = "siebert/sentiment-roberta-large-english"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
config = AutoConfig.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)


def get_biases(text):
    if text is None:
        return None
    encoded_input = tokenizer(text, return_tensors="pt")
    output = model(**encoded_input)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)

    ranking = np.argsort(scores)
    ranking = ranking[::-1]
    biases = {}
    for i in range(scores.shape[0]):
        l = config.id2label[ranking[i]]
        s = scores[ranking[i]]
        biases[l] = np.round(float(s), 4)
    return biases

df["title_sentiment_positive"] = None
df["title_sentiment_negative"] = None

print(get_biases("hello i love you"))

for index, row in df.iterrows():
    print(row["title"], type(row["title"]))
    sentiment_dict = get_biases(row["title"])
    if sentiment_dict is None:
        df.at[index, 'title_sentiment_positive'] = None 
        df.at[index, 'title_sentiment_negative'] = None 
        print("N/A")
    else:
        df.at[index, 'title_sentiment_positive'] = sentiment_dict["POSITIVE"]
        df.at[index, 'title_sentiment_negative'] = sentiment_dict["NEGATIVE"]
        print(sentiment_dict["POSITIVE"], sentiment_dict["NEGATIVE"])

df.to_csv("./link_sa.csv")
