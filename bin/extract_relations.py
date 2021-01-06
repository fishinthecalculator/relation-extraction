import os
import sys
import time
from argparse import ArgumentParser
from collections import defaultdict
from itertools import permutations
from pathlib import Path

from rdflib import Graph, URIRef

props = defaultdict(int)


def get_uri(lines):
    return map(lambda l: l.rstrip(), lines)


def export_results(tweet, sub, obj, preds, out_path):
    result_path = Path(out_path, tweet.name[:-3] + "ttl")
    preds = list(preds)
    graph = Graph()
    if len(preds) == 0:
        print(tweet.name + " contains no related entities")
        return
    for p in preds:
        props[str(p)] += 1
        graph.add((sub, p, obj))
    graph.serialize(destination=str(result_path), format="turtle")


def main(args):
    g = Graph()

    print("Loading " + str(args.dbpedia) + " ...")
    start = time.time()
    g = g.parse(location=str(args.dbpedia), format="nt")
    print("Graph loaded in " + str((time.time() - start) / 60.0) + "m.")

    for tweet in args.tweets.iterdir():
        if tweet.is_file():
            with open(tweet) as f:
                uris = get_uri(f.readlines())
            args.out_dir.mkdir(exist_ok=True, parents=True)
            for p in permutations(uris, 2):
                s = URIRef(p[0])
                o = URIRef(p[1])
                export_results(tweet,
                               s,
                               o,
                               g.predicates(s, o),
                               args.out_dir)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-t", "--tweets", type=Path, required=True,
                        help="Path of the directory of the tweets with multiple entities.")
    parser.add_argument("-d", "--dbpedia", type=Path, required=True,
                        help="Path of the nt dump of Dbpedia.")
    parser.add_argument("-o", "--out-dir", type=Path, required=True,
                        help="Directory where the n3 graphs of all the tweets that contain one or more relationships "
                             "will be exported.")
    args = parser.parse_args()
    main(args)
    for key, value in props.items():
        print(f"{key}\t{value}")
    sys.exit(0)
