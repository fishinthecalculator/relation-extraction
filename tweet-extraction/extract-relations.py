import csv
import time
from collections import defaultdict
from itertools import permutations
from pathlib import Path

from rdflib import Graph, URIRef

PROJECT = Path("/home/orang3/code/tweet-extraction")
DBPEDIA = Path(PROJECT, "mappingbased_properties_cleaned_en.nt")

props = defaultdict(int)


def get_uri(lines):
    return map(lambda l: l.rstrip().split(" ")[1], lines)


def export_results(tweet, sub, obj, preds):
    result_path = Path(PROJECT, "tweets", "with_rel", tweet.name)
    preds = list(preds)
    if len(preds) == 0:
        print(tweet.name + " contains no related entities")
    with open(result_path, "a") as res:
        for p in preds:
            props[str(p)] += 1
            res.write("<" + sub + "> " + p.n3() + " <" + obj + "> .\n")


def main():
    g = Graph()

    print("Loading " + str(DBPEDIA) + " ...")
    start = time.time()
    g = g.parse(location=str(DBPEDIA), format="nt")
    print("Graph loaded in " + str((time.time() - start) / 60.0) + "m.")

    for tweet in Path(PROJECT, "tweets").iterdir():
        if tweet.is_file():
            with open(tweet) as f:
                uris = get_uri(f.readlines())
            for p in permutations(uris, 2):
                export_results(tweet, p[0], p[1], g.predicates(URIRef(p[0]), URIRef(p[1])))


if __name__ == "__main__":
    main()
    with open(Path(PROJECT, "tweets", "props.csv"), "w") as csv_file:
        writer = csv.writer(csv_file)
        for key, value in props.items():
            writer.writerow([key, value])
