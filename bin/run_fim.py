#!/usr/bin/env python3
import os
import pickle
import sys
import time

from collections import defaultdict
from pathlib import Path

import fim
import numpy as np

this_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, this_dir)
from relext.util import make_parser, make_logger, process_stdin_or_file

logger = make_logger("run_fim")
from relext.kb.graph import load_parallel
from relext.kb.prefix import NEE, LEMON, SIOC

PROJECT_ROOT = Path(os.environ["HOME"], "code", "Thesis", "results")

FIM = Path(PROJECT_ROOT, "fim")
GRAPHS = Path(PROJECT_ROOT, "graphs")

# Support(B) = (Transactions containing (B))/(Total Transactions)
#
#
# Confidence refers to the likelihood that an item B is also bought if item A is bought
#
# Confidence(A→B) = (Transactions containing both (A and B))/(Transactions containing A)
#
#
# Lift(A -> B) refers to the increase in the ratio of sale of B when A is sold
#
# Lift(A→B) = (Confidence (A→B))/(Support (B))

uninteresting = {LEMON.writtenRep,
                 LEMON.canonicalForm,
                 NEE.hasMatchedURI,
                 NEE.detectedAs,
                 SIOC.id}


def bag_of_terms(tweet_graph):
    # BA :spouse :MA
    # bag { :BA, :spouse, :MA, ?v0-:spouse-:MA, .... }
    # the indices of the variable are progressive naturals

    # bag.append(f"{triple[0]}_{triple[1]}_X")
    # bag.append(f"X_{triple[1]}_{triple[2]}")

    # return tuple(str(term) for triple in tweet_graph.triples((None, None, None)) for term in triple)
    return [str(term)
            for triple in tweet_graph.triples((None, None, None))
            for term in triple
            if term not in uninteresting]


def bag_of_triples(tweet_graph):
    def to_n3(term):
        return term.n3(tweet_graph.namespace_manager)

    # BA :spouse :MA
    # bag { :BA, :spouse, :MA, ?v0-:spouse-:MA, .... }
    # the indices of the variable are progressive naturals

    # bag.append(f"{triple[0]}_{triple[1]}_X")
    # bag.append(f"X_{triple[1]}_{triple[2]}")
    bag = []
    for triple in tweet_graph.triples((None, None, None)):
        if triple[1] not in uninteresting:
            triple = list(map(to_n3, triple))
            bag.extend([f"{triple[0]}_{triple[1]}_{triple[2]}",
                        f"{triple[0]}_{triple[1]}_X",
                        f"X_{triple[1]}_{triple[2]}"])
    return bag


def make_bags(lines, func, bags_path):
    logger.info("Computing bags of items...")
    start = time.time()
    headers_pickle_path = Path(bags_path.parent, "headers.pickle")
    graphs = [p for p in
              (Path(GRAPHS, f"{line.strip()}.ttl")
               for line in lines)
              if p.is_file()]

    bags = [bag
            for bag in load_parallel(graphs, func)
            if len(bag) > 0]

    # Make a map of unique strings to natural numbers.
    headers = dict([(y, x + 1)
                    for x, y in enumerate(sorted(set(string
                                                     for bag in bags
                                                     for string in bag)))])
    with open(headers_pickle_path, "wb") as fp:
        pickle.dump(headers, fp)

    l = []
    for bag in bags:
        d = defaultdict(int)
        for i, string in enumerate(bag):
            d[headers[string]] += 1
            bag[i] = headers[string]
        l.append(d)

    with open(bags_path, "wb") as fp:
        pickle.dump(bags, fp)

    logger.info(f"Done in {round((time.time() - start) / 60, ndigits=2)}m")

    return bags


bag_functions = {
    "term": bag_of_terms,
    "triples": bag_of_triples
}


def main(args):
    rules_pickle_path = Path(FIM, "rules.npz")
    mapped_bags_pickle_path = Path(FIM, "mapped-bags.pickle")

    if not mapped_bags_pickle_path.is_file():
        bags = process_stdin_or_file(args, lambda l: make_bags(l,
                                                               bag_functions[args.bag_type],
                                                               mapped_bags_pickle_path))
    else:
        with open(mapped_bags_pickle_path, "rb") as fp:
            bags = pickle.load(fp)

    if not rules_pickle_path.is_file():
        logger.info("Computing association rules...")
        start = time.time()
        rules = fim.fpgrowth(bags,
                             target='r',  # Generate association rules
                             # 1e-2 -> 0G
                             # 5e-3 -> little to no ram..
                             # 4e-3 -> about 14G
                             # 3e-3 -> no way
                             # 1e-3 -> 15G and counting..
                             supp=5e-3,
                             zmin=2,
                             conf=60,  # minimum confidence of an assoc. rule
                             # C: rule confidence as a percentage
                             # a: absolute item set support (number of transactions)
                             # b: absolute body set support (number of transactions)
                             report='Cab',
                             #  eval: measure for item set evaluation
                             # q: difference of lift quotient to 1
                             # r: difference of conviction quotient to 1
                             eval='r',
                             thresh=5)  # for evaluation measure
        logger.info(f"Done in {round((time.time() - start) / 60, ndigits=2)}m")
        np.savez_compressed(rules_pickle_path, rules=rules)
    sys.exit(0)


if __name__ == "__main__":
    parser = make_parser("FIM")
    parser.add_argument("-g", "--graphs-dir", type=Path, required=True,
                        help="Path to the merged graphs representing the tweets.")
    parser.add_argument("-t", "--bag-type", type=str, default="triples",
                        help="Type of the bags that'll be used as transactions in FIM. Possible types are:\n"
                             "\t - terms"
                             "\t - triples")

    args = parser.parse_args()

    FIM = args.out_dir
    GRAPHS = args.graphs_dir

    logger.info(f"Output will be generated at {FIM}")

    main(args)
