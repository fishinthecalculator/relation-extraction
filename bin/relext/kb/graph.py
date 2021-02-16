import concurrent.futures
import time
import logging

from collections import defaultdict

from rdflib import Graph

from .prefix import all_prefixes

logger = logging.getLogger(__name__)


def sub_obj_dfs(g, node, current_level=0, max_level=10, visited=defaultdict(bool)):
    for t in g.triples((node, None, None)):
        if not visited[t]:
            visited[t] = True
            yield t
            if current_level <= (max_level - 1):
                yield from sub_obj_dfs(g, t[2],
                                       current_level=(current_level + 1),
                                       visited=visited)


def make_graph():
    graph = Graph()
    for prefix in all_prefixes:
        graph.bind(*prefix)
    return graph


def load_parallel(graphs, func=id):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(lambda tweet: func(load(tweet)), g)
                   for g in graphs]
        return [fut.result() for fut in futures]


def load(path, fmt="ttl"):
    path = str(path)
    graph = make_graph()
    logger.debug("Loading " + path + "...")
    start = time.time()
    graph.parse(location=path, format=fmt)
    logger.debug(f"Graph loaded in {round((time.time() - start) / 60, ndigits=2)}m.")

    return graph
