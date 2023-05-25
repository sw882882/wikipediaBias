import pandas as pd
import re
import ast

df_loc = pd.read_csv("./data/source/2015~.csv")
df_sources = pd.read_csv("./data/output/links.csv")

row_list = []
for index, row in df_loc.iterrows():
    dict1 = {}
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
    json_data = (row["congresses"].replace("true", "True")).replace("false", "False")
    json_data = ast.literal_eval(json_data)
    print(json_data)
    dict1.update(json_data[-1])
    dict1.update({"age": row["birthYear"]})
    dict1.update({"name": name})
    print(dict1)

    # TODO add row for domain and bias in df_sources wikipedia_scrape.py then write pandas code to get data for box and whiskers
    # nvm no need

    row_list.append(dict1)
df = pd.DataFrame(row_list)
print(df)

df.to_csv("test.csv")
