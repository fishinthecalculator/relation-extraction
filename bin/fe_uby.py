#!/usr/bin/env python3

import os
import sys

from pathlib import Path

this_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, this_dir)
from util import make_parser, process_stdin_or_file
from kb.fe import UbyFE


def main(args):
    with open(args.split_file) as fp:
        split_token = fp.read()

    fe = UbyFE(args.uby, args.out_dir, args.tweets, split_token, args.n_hops)
    fe.load_data("nt")

    process_stdin_or_file(args, fe.process_tweets)

    sys.exit(0)


if __name__ == "__main__":
    parser = make_parser("UBY")

    parser.add_argument("-n", "--n-hops", type=int, default=10,
                        help="The number of hops to explore from each node.")
    parser.add_argument("-t", "--tweets", type=Path, required=True,
                        help="Path of the directory of the tweets with multiple entities.")
    parser.add_argument("-f", "--split-file", type=Path, required=True,
                        help="Path of the file containing the split token.")
    parser.add_argument("-u", "--uby", type=Path, required=True,
                        help="Path of the nt dump of UBY.")

    args = parser.parse_args()

    main(args)
