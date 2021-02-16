import asyncio
import os
import sys
from pathlib import Path

this_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, this_dir)
from relext.util import make_logger, make_parser, process_stdin_or_file

logger = make_logger("merge_graphs")
from relext.kb.graph import load, make_graph

PROJECT_ROOT = Path(os.environ["HOME"], "code", "Thesis")
GRAPHS = Path(PROJECT_ROOT, "results", "graphs")

UBY_NEIGHBORS = Path(PROJECT_ROOT, "results", "uby-neighbors")
DBPEDIA_NEIGHBORS = Path(PROJECT_ROOT, "results", "related")
TWEETSKB_NEIGHBORS = Path(PROJECT_ROOT, "results", "entities")


def is_empty(iterable):
    try:
        next(iterable)
    except StopIteration:
        return True
    return False


async def merge_graphs(tweet_id):
    tweet_graph = make_graph()
    loop = asyncio.get_running_loop()

    # Merge tweet graphs.
    datasets = [UBY_NEIGHBORS,
                DBPEDIA_NEIGHBORS,
                TWEETSKB_NEIGHBORS]
    for d in datasets:
        triples = Path(d, f"{tweet_id}.ttl")
        if triples.is_file():
            tweet_graph = await loop.run_in_executor(None, load, triples)
        else:
            logger.debug(f"{triples} is not a file!")

    if not is_empty(tweet_graph.triples((None, None, None))):
        export = lambda i: tweet_graph.serialize(destination=str(Path(GRAPHS, f"{i}.ttl")),
                                                 encoding="utf-8",
                                                 format="ttl")
        await loop.run_in_executor(None, export, tweet_id)


async def main(args):
    loop = asyncio.get_running_loop()
    lines = await loop.run_in_executor(None, process_stdin_or_file, args)
    await asyncio.gather(*(merge_graphs(l.strip()) for l in lines))


if __name__ == "__main__":
    parser = make_parser("merge-graphs")
    parser.add_argument("-t", "--tweetskb", type=Path, required=True,
                        help="Path of the TweetsKB graphs representing the tweets.")
    parser.add_argument("-d", "--dbpedia", type=Path, required=True,
                        help="Path of the Dbpedia graphs representing the entities.")
    parser.add_argument("-u", "--uby", type=Path, required=True,
                        help="Path of the graphs of the neighbors of all the tokens in a tweet.")

    args = parser.parse_args()

    GRAPHS = args.out_dir

    UBY_NEIGHBORS = args.uby
    DBPEDIA_NEIGHBORS = args.dbpedia
    TWEETSKB_NEIGHBORS = args.tweetskb

    logger.info(f"Output will be saved at {GRAPHS}")

    asyncio.run(main(args))
    sys.exit(0)
