from argparse import ArgumentParser
import os
import sys
from pathlib import Path
from rdflib import Graph

this_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, this_dir)
from relext.kb.graph import load

PROJECT_ROOT = Path(os.environ["HOME"], "code", "Thesis")
GRAPHS = Path(PROJECT_ROOT, "results", "graphs")

UBY_NEIGHBORS = Path(PROJECT_ROOT, "results", "uby-neighbors")
DBPEDIA_NEIGHBORS = Path(PROJECT_ROOT, "results", "related")
TWEETSKB_NEIGHBORS = Path(PROJECT_ROOT, "results", "entities")


def is_empty(iterable):
    try:
        next(iterable)
    except StopIteration:
        return True
    return False


def merge_graphs(tweet_id):
    tweet_graph = Graph()

    # Merge tweet graphs.
    datasets = [UBY_NEIGHBORS,
                DBPEDIA_NEIGHBORS,
                TWEETSKB_NEIGHBORS]
    for d in datasets:
        triples = Path(d, f"{tweet_id}.ttl")
        if triples.is_file():
            tweet_graph = load(triples, fmt="turtle")
        else:
            print(f"{triples} is not a file!")

    if not is_empty(tweet_graph.triples((None, None, None))):
        tweet_graph.serialize(destination=str(
            Path(GRAPHS, f"{tweet_id}.ttl")), encoding="utf-8", format="ttl")


def main(args):
    merge_graphs(args.id)
    sys.exit(0)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-i", "--id", type=str, required=True,
                        help="Tweet ID.")
    parser.add_argument("-o", "--out-dir", type=Path, required=True,
                        help="Path to the directory where the graphs will be exported to.")
    parser.add_argument("-t", "--tweetskb", type=Path, required=True,
                        help="Path of the TweetsKB graphs representing the tweets.")
    parser.add_argument("-d", "--dbpedia", type=Path, required=True,
                        help="Path of the Dbpedia graphs representing the entities.")
    parser.add_argument("-u", "--uby", type=Path, required=True,
                        help="Path of the graphs of the neighbors of all the tokens in a tweet.")

    args = parser.parse_args()

    GRAPHS = args.out_dir

    UBY_NEIGHBORS = args.uby
    DBPEDIA_NEIGHBORS = args.dbpedia
    TWEETSKB_NEIGHBORS = args.tweetskb

    print(f"Output will be generated at {GRAPHS}/{args.id}.ttl")

    main(args)
