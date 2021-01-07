import time
from collections import defaultdict

from rdflib import Graph

from rdflib.namespace import NamespaceManager

from .prefix import all_prefixes


def sub_obj_dfs(g, node, current_level=0, max_level=10, visited=defaultdict(bool)):
    for t in g.triples((node, None, None)):
        if not visited[t]:
            visited[t] = True
            yield t
            if current_level <= (max_level - 1):
                yield from sub_obj_dfs(g, t[2],
                                       current_level=(current_level + 1),
                                       visited=visited)


def load(path, fmt="turtle"):
    path = str(path)
    graph = Graph()
    for prefix in all_prefixes:
        graph.bind(*prefix)
    print("Loading " + path + "...")
    start = time.time()
    graph.parse(location=path, format=fmt)
    print(f"Graph loaded in {round((time.time() - start) / 60, ndigits=2)}m.")

    return graph
