import sys
from argparse import ArgumentParser
from pathlib import Path

from relext.kb.fe import TweetsKbFE, UbyFE, DbpediaFE

make_extractor = {
    "tweetskb": lambda args: TweetsKbFE(args.tweetskb, args.out_dir),
    "uby": lambda args: UbyFE(args.uby, args.out_dir, args.tweets, args.split_file, args.n_hops),
    "dbpedia": lambda args: DbpediaFE(args.dbpedia, args.out_dir, args.tweets)
}


def make_parser(dataset):
    parser = ArgumentParser()
    parser.add_argument("-i", "--tweet-ids", type=Path, required=True,
                        help="Path of the TSV file listing the tweet ids.")
    parser.add_argument("--stdin", type=bool, default=False,
                        help="Read ids from stdin instead of the TSV file.")
    parser.add_argument("-o", "--out-dir", type=Path, required=True,
                        help=f"Directory where the feature graphs from {dataset} "
                             "will be exported.")
    return parser


def augment_parser(source, parser):
    if source == "tweetskb":
        parser.add_argument("-t", "--tweetskb", type=Path, required=True,
                            help="Path of the nt dump of TweetsKB.")
    elif source == "uby":
        parser.add_argument("-n", "--n-hops", type=int, default=10,
                            help="The number of hops to explore from each node.")
        parser.add_argument("-t", "--tweets", type=Path, required=True,
                            help="Path of the directory of the tweets with multiple entities.")
        parser.add_argument("-f", "--split-file", type=Path, required=True,
                            help="Path of the file containing the split token.")
        parser.add_argument("-u", "--uby", type=Path, required=True,
                            help="Path of the nt dump of UBY.")
    elif source == "dbpedia":
        parser.add_argument("-t", "--tweets", type=Path, required=True,
                            help="Path of the directory of the tweets with multiple entities.")
        parser.add_argument("-d", "--dbpedia", type=Path, required=True,
                            help="Path of Dbpedia's dump.")
    else:
        raise ValueError(f"source must be one of {make_extractor.keys()}")
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
