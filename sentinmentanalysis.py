from transformers import pipeline

sentiment_analysis = pipeline(
    "sentiment-analysis", model="siebert/sentiment-roberta-large-english"
)

text = """
In the two years since the attack on the US Capitol, the Fox primetime host used his huge platform to amplify paper-thin theories that the attack was a false-flag operation orchestrated by the FBI and government agents because they loathed Trump, and that the criminal rioters were themselves the victims.
"""
print(sentiment_analysis(text))
