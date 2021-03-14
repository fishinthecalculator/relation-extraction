import concurrent.futures
import time
import logging

from collections import defaultdict

from rdflib import Graph

from .prefix import all_prefixes

logger = logging.getLogger(__name__)


def sub_obj_bfs(g, node, max_level=10):
    visited = defaultdict(int)
    border = [(node, 0)]
    while len(border) > 0:
        n, l = border.pop(0)
        for t in g.triples((n, None, None)):
            yield t
            if not visited[t[2]]:
                visited[t[2]] = True
                if l <= (max_level - 1):
                    border.append((t[2], l + 1))


def sub_obj_dfs(g, node, current_level=0, max_level=10, visited=None):
    if visited is None:
        visited = defaultdict(bool)
    for t in g.triples((node, None, None)):
        yield t
        if not visited[t[2]]:
            visited[t[2]] = True
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
                   for g in graphs if g.is_file()]
        return [fut.result() for fut in futures]


def load(path, fmt="ttl"):
    path = str(path)
    graph = make_graph()
    logger.debug("Loading " + path + "...")
    start = time.time()
    graph.parse(location=path, format=fmt)
    logger.debug(f"Graph loaded in {round((time.time() - start) / 60, ndigits=2)}m.")

    return graph
