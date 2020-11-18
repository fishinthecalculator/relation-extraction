import time
from collections import defaultdict
from pathlib import Path

from rdflib import Graph, URIRef

PROJECT = Path("/home/orang3/code/Thesis/babelnet")
BABEL = Path(PROJECT, "babel-synset")

prop_counter = defaultdict(int)

def main():
    g = Graph()

    print("Loading " + str(BABEL) + " ...")
    start = time.time()
    for f in BABEL.iterdir():
        g.parse(location=str(f), format="nt")
    print("Graph loaded in " + str(time.time() - start) + "s.")

    for s, p, o in g:
        prop_counter[p] += 1

    for prop, count in sorted(prop_counter.items(), key=lambda i: i[1], reverse=True):
        print(f"{prop},{count}")
    

if __name__ == "__main__":
    main()
