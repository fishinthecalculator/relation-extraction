import asyncio
import logging
import pickle
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from itertools import permutations
from pathlib import Path

from rdflib import Literal, URIRef
from rdflib.util import guess_format

from .graph import make_graph, sub_obj_bfs, is_empty_graph
from .prefix import NEE, SIOC, SCHEMA, LEMON

logger = logging.getLogger(__name__)


def cut(strings, field: int, sep="\t"):
    """
    Implements the cut command.
    Parameters
    ----------
    strings: List of strings to cut.
    field: Column to select.
    sep: Separation token.

    Returns
    -------
    Generator of the nth fields of the input strings, splitted by sep.
    """
    return list(string.rstrip().split(sep)[field] for string in strings)


class FeatureExtractor(ABC):
    def __init__(self, data_path: Path, out_path: Path, split_token=" ", fmt=""):
        self.data_path = data_path
        self.out_path = out_path
        self.data_is_loaded = False
        self._processed = set()
        self.g = make_graph()

        if not fmt:
            self.fmt = guess_format(str(self.data_path))
        else:
            self.fmt = fmt

        if isinstance(split_token, Path):
            with open(split_token) as fp:
                self.split_token = fp.read()
        elif type(split_token) == str:
            self.split_token = split_token
        else:
            raise TypeError("split_token should be either str or Path!")

        super().__init__()

    def load_data(self):
        if not self.data_is_loaded:
            data_pickled = Path(f"{self.data_path}.pickle")
            if data_pickled.is_file():
                logger.info(f"Loading {data_pickled}...")
                with open(data_pickled, "rb") as fp:
                    self.g = pickle.load(fp)
            else:
                graph = make_graph()
                start = time.time()

                logger.info(f"Loading {self.data_path}...")
                self.g = graph.parse(location=str(self.data_path), format=self.fmt)
                logger.info(
                    f"Graph loaded in {round((time.time() - start) / 60, ndigits=2)}m."
                )

                try:
                    with open(data_pickled, "wb") as fp:
                        pickle.dump(self.g, fp)
                except OSError as e:
                    logger.error(e.strerror)

            self.data_is_loaded = True

    @abstractmethod
    def _extract(self, tweet_id):
        pass

    def extract(self, tweet_id):
        assert (
            self.data_is_loaded
        ), f"{self.data_path} has not been loaded! You MUST call `{type(self)}.load_data()` !"
        return self._extract(tweet_id)

    async def extract_export(self, tweet_id, i, l):
        loop = asyncio.get_running_loop()
        if tweet_id not in self._processed:
            logger.debug(f"{type(self)} - [{i}/{l}] Extracting {tweet_id} features...")

            def try_to_log(msg):
                try:
                    logger.info(msg)
                except OSError:
                    print("CRITICAL - Couldn't log to file!")

            await loop.run_in_executor(
                None,
                try_to_log,
                f"Extracting {tweet_id} features from {self.data_path}...",
            )
            graph = self.extract(tweet_id)
            self._processed.add(tweet_id)
            if (graph is not None) and (not is_empty_graph(graph)):
                await self.export(graph, tweet_id)
        else:
            await loop.run_in_executor(
                None,
                logger.warning,
                f"{type(self)} - duplicate tweet {tweet_id} in input stream...",
            )

    async def export(self, graph, tweet_id, fmt="turtle"):
        loop = asyncio.get_running_loop()
        export = lambda i: graph.serialize(
            destination=str(Path(self.out_path, f"{tweet_id}.ttl")),
            encoding="utf-8",
            format=fmt,
        )
        await loop.run_in_executor(None, export, tweet_id)


class DbpediaFE(FeatureExtractor):
    def __init__(
            self, data_path: Path, out_path: Path, tweets_path: Path, max_level=3, fmt="nt"
    ):
        super().__init__(data_path, out_path, fmt=fmt)
        self.props = defaultdict(int)
        self.tweets_path = tweets_path
        self.max_level = max_level

    @staticmethod
    def get_uris(tweet):
        with open(tweet) as f:
            uris = cut(f.readlines(), 0)
        return uris

    def _extract(self, tweet_id):
        graph = make_graph()
        graph_path = Path(self.tweets_path, f"{tweet_id}.tsv")
        if graph_path.is_file():
            uris = DbpediaFE.get_uris(graph_path)
            if 0 < len(uris) < 2:
                # Add n-hops neighbors.
                for t in sub_obj_bfs(self.g, uris[0], max_level=self.max_level):
                    graph.add(t)
            elif len(uris) >= 2:
                for perm in permutations(uris, 2):
                    sub = URIRef(perm[0])
                    obj = URIRef(perm[1])

                    # Add all relations between sub and obj.
                    for p in self.g.predicates(sub, obj):
                        self.props[str(p)] += 1
                        graph.add((sub, p, obj))

                    # Add n-hops neighbors.
                    for node in (sub, obj):
                        for t in sub_obj_bfs(self.g, node, max_level=self.max_level):
                            graph.add(t)

        return graph


class UbyFE(FeatureExtractor):
    def __init__(
            self,
            data_path: Path,
            out_path: Path,
            entities_path: Path,
            split_token=" ",
            max_level=3,
            fmt="nt",
    ):
        super().__init__(data_path, out_path, split_token=split_token, fmt=fmt)
        self.entities_path = entities_path
        self.max_level = max_level

    @staticmethod
    def get_tokens(tweet):
        with open(tweet) as f:
            tokens = cut(f.readlines(), 1)
        return tokens

    def _extract(self, tweet_id):
        graph = make_graph()
        graph_path = Path(self.entities_path, f"{tweet_id}.tsv")
        if graph_path.is_file():
            words = (
                splitted
                for token in UbyFE.get_tokens(graph_path)
                for splitted in token.split(self.split_token)
            )

            for word in words:
                rep = Literal(word)

                # Add canonical forms of tokens.
                for canonical_form in self.g.subjects(LEMON.writtenRep, rep):
                    graph.add((canonical_form, LEMON.writtenRep, rep))

                    # Add each sense of the canonical form.
                    for sense in self.g.subjects(LEMON.canonicalForm, canonical_form):
                        graph.add((sense, LEMON.canonicalForm, canonical_form))

                        # Add n-hops neighbors.
                        for t in sub_obj_bfs(self.g, sense, max_level=self.max_level):
                            graph.add(t)
        return graph


class TweetsKbFE(FeatureExtractor):
    def __init__(self, data_path: Path, out_path: Path, fmt="n3"):
        super().__init__(data_path, out_path, fmt=fmt)

    def _extract(self, tweet_id):
        tweet_graph = make_graph()
        for post in self.g.subjects(SIOC.id, Literal(tweet_id)):
            for entity in self.g.objects(post, SCHEMA.mentions):
                # Detected entity Dbpedia URI.
                for uri in self.g.objects(entity, NEE.hasMatchedURI):
                    tweet_graph.add((entity, NEE.hasMatchedURI, uri))

                # Token from which the Dbpedia entity has been detected.
                for rep in self.g.objects(entity, NEE.detectedAs):
                    tweet_graph.add((entity, NEE.detectedAs, rep))
        return tweet_graph
