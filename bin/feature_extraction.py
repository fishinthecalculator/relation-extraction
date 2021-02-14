import os
import sys

this_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, this_dir)
from relext.util import make_parser, process_stdin_or_file, augment_parser, make_extractor


def main(args):
    fe = make_extractor[args.source](args)
    fe.load_data()

    process_stdin_or_file(args, fe.process_tweets)

    sys.exit(0)


if __name__ == "__main__":
    parser = make_parser("feature-extraction")
    parser.add_argument("-s", "--source", type=str, required=True,
                        help="Data source to extract features from. "
                             f"It must be one of \n{make_extractor.keys()}")
    args, rest = parser.parse_known_args()
    parser = augment_parser(args.source, parser)
    args = parser.parse_args()
    main(args)

    sys.exit(0)
