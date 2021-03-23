#!/usr/bin/env python3

import concurrent.futures
import os
import pickle
import sys
from pathlib import Path

this_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, this_dir)
from relext.util import make_logger, make_parser, process_stdin_or_file

logger = make_logger("merge_graphs")
from relext.kb.prefix import NEE, LEMON, SIOC
from relext.kb.graph import load, make_graph, is_empty_graph

PROJECT_ROOT = Path(os.environ["HOME"], "code", "Thesis")
GRAPHS = Path(PROJECT_ROOT, "results", "graphs")

UBY_NEIGHBORS = Path(PROJECT_ROOT, "results", "uby-neighbors")
DBPEDIA_NEIGHBORS = Path(PROJECT_ROOT, "results", "related")
TWEETSKB_NEIGHBORS = Path(PROJECT_ROOT, "results", "entities")

uninteresting_terms = {
    LEMON.writtenRep,
    LEMON.canonicalForm,
    NEE.hasMatchedURI,
    NEE.detectedAs,
    SIOC.id,
}
uninteresting_triples = {SIOC.id, NEE.hasMatchedURI, NEE.detectedAs}


class Environment:
    def __init__(self):
        self.mappings = {}
        self.idx = 0

    def lookup(self, node):
        if node not in self.mappings.keys():
            self.mappings[node] = f"?v{self.idx}"
            self.idx += 1
        return self.mappings[node]


def bag_of_terms(tweet_graph):
    def to_n3(term):
        return term.n3(tweet_graph.namespace_manager)

    # BA :spouse :MA
    # bag { :BA, :spouse, :MA, ?v0-:spouse-:MA, .... }
    # the indices of the variable are progressive naturals

    # bag.append(f"{triple[0]}_{triple[1]}_X")
    # bag.append(f"X_{triple[1]}_{triple[2]}")

    # return tuple(str(term) for triple in tweet_graph.triples((None, None, None)) for term in triple)
    bag = []
    env = Environment()
    for triple in tweet_graph.triples((None, None, None)):
        bag.extend([to_n3(t) for t in triple if (t not in uninteresting_terms)  # and (not isinstance(t, Literal))
                    ])
        if triple[1] not in uninteresting_triples:
            terms = [to_n3(t) for t in triple]
            bag.extend(
                [
                    #  f"{triple[0]}_{triple[1]}_{env.lookup(triple[2])}",
                    f"{env.lookup(terms[0])}_{terms[1]}_{terms[2]}"
                ]
            )
    return bag


def bag_of_triples(tweet_graph):
    def to_n3(term):
        return term.n3(tweet_graph.namespace_manager)

    # BA :spouse :MA
    # bag { :BA, :spouse, :MA, ?v0-:spouse-:MA, .... }
    # the indices of the variable are progressive naturals

    # bag.append(f"{triple[0]}_{triple[1]}_X")
    # bag.append(f"X_{triple[1]}_{triple[2]}")
    bag = []
    env = Environment()
    for triple in tweet_graph.triples((None, None, None)):
        if triple[1] not in uninteresting_triples:
            triple = [to_n3(t) for t in triple]
            bag.append(f"{triple[0]}_{triple[1]}_{triple[2]}")
            bag.extend(
                [
                    f"{triple[0]}_{triple[1]}_{env.lookup(triple[2])}",
                    # f"X_{triple[1]}_{triple[2]}"
                ]
            )
    return bag


bag_functions = {"term": bag_of_terms, "triples": bag_of_triples}


def p_dump(obj, path):
    with open(path, "wb") as fp:
        pickle.dump(obj, fp)


def merge_graphs(tweet_id, b_type, idx, length):
    def export(t_graph, t_id, t_bag):
        if not is_empty_graph(t_graph):
            p_dump(t_bag,
                   Path(GRAPHS, f"{t_id}.pickle"))
            t_graph.serialize(destination=str(Path(GRAPHS, f"{t_id}.ttl")),
                              encoding="utf-8",
                              format="ttl")

    tweet_graph = make_graph()

    # Merge tweet graphs.
    datasets = [UBY_NEIGHBORS,
                DBPEDIA_NEIGHBORS]

    logger.debug(f"[{idx}/{length}] - Computing {tweet_id}'s bag...")

    for d in datasets:
        triples = Path(d, f"{tweet_id}.ttl")
        if triples.is_file():
            tweet_graph = load(triples, graph=tweet_graph, fmt="text/turtle")

    export(tweet_graph,
           tweet_id,
           bag_functions[b_type](tweet_graph))


def main(args):
    lines = process_stdin_or_file(args)
    l = len(lines)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(merge_graphs, line.strip(), args.bag_type, i + 1, l)
                   for i, line in enumerate(lines)]
        return [fut.result() for fut in futures]


if __name__ == "__main__":
    parser = make_parser("merge-graphs")
    parser.add_argument("-d", "--dbpedia", type=Path, required=True,
                        help="Path of the Dbpedia graphs representing the entities.")
    parser.add_argument("-u", "--uby", type=Path, required=True,
                        help="Path of the graphs of the neighbors of all the tokens in a tweet.")
    default_bag_fun = [name for name, _ in bag_functions.items()][0]
    bag_function_names = ', '.join(name for name, _ in bag_functions.items())
    parser.add_argument(
        "-b",
        "--bag-type",
        type=str,
        default=default_bag_fun,
        help="Type of the bags that'll be used as transactions in FIM. Possible types are:\n"
             f"{bag_function_names}."
    )

    args = parser.parse_args()

    GRAPHS = args.out_dir

    UBY_NEIGHBORS = args.uby
    DBPEDIA_NEIGHBORS = args.dbpedia
    # TWEETSKB_NEIGHBORS = args.tweetskb

    logger.info(f"Output will be saved at {GRAPHS}")

    main(args)
    sys.exit(0)
