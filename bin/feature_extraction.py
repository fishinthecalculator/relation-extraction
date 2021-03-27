#!/usr/bin/env python3

import os
import sys

this_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, this_dir)
from relext.util import make_parser, make_logger, process_stdin_or_file, fe_parser, make_extractor


def main(args):
    logger = make_logger("feature_extraction_" + args.source)
    logger.info(f"Extracting features from {args.source}...")
    fe = make_extractor[args.source](args)
    fe.load_data()

    lines = process_stdin_or_file(args)
    n_lines = len(lines)
    logger.info(f"Processing {n_lines} tweets...")
    for i, tweet_id in enumerate(lines):
        fe.extract_export(tweet_id.strip(), i + 1, n_lines)
    logger.info(f"Exported features from {len(list(args.out_dir.glob('*.ttl')))} tweets.")


if __name__ == "__main__":
    parser = make_parser("feature-extraction")
    parser.add_argument("-s", "--source", type=str, required=True,
                        help="Data source to extract features from. "
                             f"It must be one of \n{make_extractor.keys()}")
    args, rest = parser.parse_known_args()
    parser = fe_parser(args.source, parser)
    args = parser.parse_args()
    main(args)
    sys.exit(0)
