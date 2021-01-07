import os
import sys
from pathlib import Path

this_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, this_dir)
from util import make_parser, process_stdin_or_file
from kb.fe import TweetsKbFE


def main(args):
    fe = TweetsKbFE(args.tweetskb, args.out_dir)
    fe.load_data("n3")

    process_stdin_or_file(args, fe.process_tweets)


if __name__ == "__main__":
    parser = make_parser("TweetsKB")
    parser.add_argument("-t", "--tweetskb", type=Path, required=True,
                        help="Path of the nt dump of TweetsKB.")
    args = parser.parse_args()
    main(args)

    sys.exit(0)
