import os
import sys

from pathlib import Path

this_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, this_dir)
from util import make_parser, process_stdin_or_file
from kb.fe import DbpediaFE


def main(args):
    fe = DbpediaFE(args.dbpedia, args.out_dir, args.tweets)
    fe.load_data("nt")

    process_stdin_or_file(args, fe.process_tweets)

    for key, value in fe.props.items():
        print(f"{key}\t{value}")
    sys.exit(0)


if __name__ == "__main__":
    parser = make_parser("Dbpedia")
    parser.add_argument("-t", "--tweets", type=Path, required=True,
                        help="Path of the directory of the tweets with multiple entities.")
    parser.add_argument("-d", "--dbpedia", type=Path, required=True,
                        help="Path of Dbpedia's dump.")

    args = parser.parse_args()
    main(args)
