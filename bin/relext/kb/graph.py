import asyncio
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


def read_graph(path):
    with open(path) as fp:
        return fp.read()


async def load(path, graph=None, fmt="text/turtle"):
    loop = asyncio.get_running_loop()
    if graph is None:
        graph = make_graph()
    graph_str = await loop.run_in_executor(None, read_graph, path)
    return graph.parse(data=graph_str, format=fmt)


def is_empty_graph(graph):
    iterable = graph.triples((None, None, None))
    try:
        next(iterable)
    except StopIteration:
        return True
    return False
