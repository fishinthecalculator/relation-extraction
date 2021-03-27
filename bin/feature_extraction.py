#!/usr/bin/env python3

import asyncio
import os
import sys

this_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, this_dir)
from relext.util import (
    make_parser,
    make_logger,
    process_stdin_or_file,
    fe_parser,
    make_extractor,
)


async def main(args):
    logger = make_logger("feature_extraction_" + args.source)
    logger.info(f"Extracting features from {args.source}...")
    fe = make_extractor[args.source](args)
    fe.load_data()

    loop = asyncio.get_running_loop()
    lines = await loop.run_in_executor(None, process_stdin_or_file, args)
    l = len(lines)
    await asyncio.gather(*(fe.extract_export(tweet_id.strip(), i + 1, l) for i, tweet_id in enumerate(lines)))
    logger.info(f"Exported features from {args.source} to {args.out_dir}")


if __name__ == "__main__":
    parser = make_parser("feature-extraction")
    parser.add_argument(
        "-s",
        "--source",
        type=str,
        required=True,
        help="Data source to extract features from. "
             f"It must be one of \n{make_extractor.keys()}",
    )
    args, rest = parser.parse_known_args()
    parser = fe_parser(args.source, parser)
    args = parser.parse_args()
    asyncio.run(main(args))
    sys.exit(0)
