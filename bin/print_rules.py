#!/usr/bin/env python3

import os
import pickle
import sys
from argparse import ArgumentParser
from pathlib import Path

import numpy as np

this_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, this_dir)
from relext.util import make_logger


def restore_headers(rule, headers):
    return headers[rule[0]], [headers[item] for item in rule[1]], *rule[2:]


def main(args):
    logger = make_logger("print_rules")
    rules_npz = np.load(args.rules, allow_pickle=True)
    rules = rules_npz['rules']
    with open(Path(args.rules.parent, "headers.pickle"), "rb") as fp:
        headers = pickle.load(fp)
    inv_headers = {v: k for k, v in headers.items()}

    #  a list of rules (i.e. tuples with two or more elements), each consisting of

    #  - a head/consequent item, a tuple with
    #  - a body/antecedent item set
    #  - the values selected by the parameter 'report', which may be combined into a
    #    tuple or a list if report[0] is '(' or '[', respectively.
    mapped_rules = np.array(list(map(lambda r: restore_headers(r, inv_headers), rules)))
    np.savetxt(Path(args.rules.parent, "rules.txt"), mapped_rules, fmt='%s')
    sys.exit(0)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-r", "--rules", type=Path, required=True,
                        help="Path to the generated rules .pickle serialization.")

    args = parser.parse_args()

    main(args)
