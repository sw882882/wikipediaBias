from duckduckgo_search import ddg

r = ddg("Ralph Abraham politician site:en.wikipedia.org")

print(r[0]["href"])
