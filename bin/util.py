import itertools
import sys
from argparse import ArgumentParser
from pathlib import Path


def make_parser(dataset):
    parser = ArgumentParser()
    parser.add_argument("-i", "--tweet-ids", type=Path, required=True,
                        help="Path of the TSV file listing the tweet ids.")
    parser.add_argument("-s", "--stdin", type=bool, default=False,
                        help="Read ids from stdin instead of the TSV file.")
    parser.add_argument("-o", "--out-dir", type=Path, required=True,
                        help=f"Directory where the feature graphs from {dataset} "
                             "will be exported.")
    return parser


def process_stdin_or_file(args, func):
    if args.stdin:
        return func(sys.stdin)
    else:
        if args.tweet_ids.is_dir():
            ids = Path(args.tweet_ids, "ids.tsv")
        else:
            ids = args.tweet_ids
        with open(ids) as fp:
            return func(fp)