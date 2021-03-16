#!/usr/bin/env python3
import os
import pickle
import sys
import time
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path

import fim
import numpy as np

this_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, this_dir)
from relext.util import make_logger

logger = make_logger("run_fim")
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

def p_load(path):
    with open(path, "rb") as fp:
        return pickle.load(fp)


def map_bags(bags_path):
    headers_pickle_path = Path(bags_path.parent, f"headers.pickle")
    start = time.time()
    logger.info("Loading bags of items...")
    bags = [bag for bag in map(p_load, GRAPHS.glob("*.pickle")) if len(bag) > 0]

    logger.info("Enumerating unique items...")
    # Make a map of unique strings to natural numbers.
    headers = dict(
        [
            (y, x + 1)
            for x, y in enumerate(sorted(set(string for bag in bags for string in bag)))
        ]
    )
    with open(headers_pickle_path, "wb") as fp:
        pickle.dump(headers, fp)

    logger.info("Mapping bag items...")
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


def main(args):
    rules_pickle_path = Path(FIM, f"rules.npz")
    mapped_bags_pickle_path = Path(FIM, f"mapped-bags.pickle")

    if not mapped_bags_pickle_path.is_file():
        bags = map_bags(mapped_bags_pickle_path)
    else:
        with open(mapped_bags_pickle_path, "rb") as fp:
            bags = pickle.load(fp)

    if not rules_pickle_path.is_file():
        logger.info("Computing association rules...")
        start = time.time()
        rules = fim.fpgrowth(
            bags,
            target="r",  # Generate association rules
            # 1e-2 -> 0G
            # 5e-3 -> little to no ram..
            # 4e-3 -> about 14G
            # 3e-3 -> no way
            # 1e-3 -> 15G and counting..
            supp=1e-3,
            zmin=2,
            conf=60,  # minimum confidence of an assoc. rule
            # C: rule confidence as a percentage
            # a: absolute item set support (number of transactions)
            # b: absolute body set support (number of transactions)
            report="Cab",
            #  eval: measure for item set evaluation
            # q: difference of lift quotient to 1
            # r: difference of conviction quotient to 1
            eval="r",
            thresh=5,
        )  # for evaluation measure
        logger.info(f"Done in {round((time.time() - start) / 60, ndigits=2)}m")
        np.savez_compressed(rules_pickle_path, rules=rules)
    sys.exit(0)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-o", "--out-dir", type=Path, required=True,
                        help=f"Directory where the output from FIM "
                             "will be saved.")
    parser.add_argument(
        "-g",
        "--graphs-dir",
        type=Path,
        required=True,
        help="Path to the merged graphs representing the tweets.",
    )

    args = parser.parse_args()

    FIM = args.out_dir
    GRAPHS = args.graphs_dir

    logger.info(f"Output will be generated at {FIM}")

    main(args)
