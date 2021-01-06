#!/usr/bin/env python3

import csv
import time

from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path

from rdflib import Graph, Namespace, Literal

PROJECT = Path("/home/orang3/code/Thesis/UBY")
UBY = Path(PROJECT, "vn.nt")

g = Graph()

SPLIT_TOKEN = " "
LEMON = Namespace("http://www.monnet-project.eu/lemon#")


def visit_tweet_graph(node, current_level=0, max_level=10, visited=defaultdict(bool)):
    for t in g.triples((node, None, None)):
        if not visited[t]:
            visited[t] = True
            yield t
            if current_level <= (max_level - 1):
                yield from visit_tweet_graph(t[2],
                                             current_level=(current_level + 1),
                                             visited=visited)


def uby_triples(tweet_graph, rep, max_level):
    rep = Literal(rep)
    for canonical_form in g.subjects(LEMON.writtenRep, rep):
        tweet_graph.add((canonical_form, LEMON.writtenRep, rep))
        for sense in g.subjects(LEMON.canonicalForm, canonical_form):
            tweet_graph.add((sense, LEMON.canonicalForm, canonical_form))
            for t in visit_tweet_graph(sense, max_level=max_level):
                tweet_graph.add(t)
    return tweet_graph


def export_graph(args, tweet_id, rep):
    rep_graph = Graph()
    rep_graph = uby_triples(rep_graph, rep, args.n_hops)
    ser = rep_graph.serialize(destination=str(Path(args.out_dir, f"{tweet_id}.ttl")),
                              format="ttl")
    if ser is not None:
        ser.decode("utf-8")
    else:
        print(f"ERROR! {tweet_id}'s graph is None.")


def main(args):
    with open(args.entities_file) as fp:
        reader = csv.reader(fp, delimiter="\t")
        for i, line in enumerate(reader):
            assert len(
                line) == 4, f'Line {i + 1} from {args.entities_file} contains {len(line)} cells:\n{" ".join(line)}'
            tweet_id, e, uri, rep = line
            for token in rep.split(SPLIT_TOKEN):
                export_graph(args, tweet_id, token)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-n", "--n-hops", type=int, default=10,
                        help="The number of hops to explore from each node.")
    parser.add_argument("-e", "--entities-file", type=Path, required=True,
                        help="Path of TSV file containing the tweets and entities.")
    parser.add_argument("-s", "--split-file", type=Path, required=True,
                        help="Path of the file containing the split token.")
    parser.add_argument("-u", "--uby", type=Path, required=True,
                        help="Path of the nt dump of UBY.")
    parser.add_argument("-o", "--out-dir", type=Path, required=True,
                        help="Directory where the Turtle graphs of all the tweets that contain one or more "
                             "relationships will be exported.")

    args = parser.parse_args()
    UBY = args.uby
    with open(args.split_file) as fp:
        SPLIT_TOKEN = fp.read()

    print("Loading " + str(UBY) + " ...")
    start = time.time()
    g = g.parse(location=str(UBY), format="nt")
    print("Graph loaded in " + str(time.time() - start) + "s.")

    main(args)
