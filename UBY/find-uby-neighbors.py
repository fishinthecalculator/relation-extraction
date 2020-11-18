import time
from pathlib import Path

from rdflib import Graph, URIRef

PROJECT = Path("/home/orang3/code/Thesis/UBY")
UBY = Path(PROJECT, "vn.nt")


def export_results(neighborhood):
    result_path = Path(PROJECT, "uby-neighbors.nt")
    with open(result_path, "w") as res:
        res.write(neighborhood.serialize(format="nt").decode("utf-8"))


# Two hops neighbors
def get_neighbors(g, token_id):
    sub = URIRef(f"http://lemon-model.net/lexica/uby/vn/{token_id.strip()}")
    print(f"subject: {sub}")
    for s, p, o in g.triples((sub, None, None)):
        yield s, p, o
        print(f"\tneighbor: {o}")
        for s2, p2, o2 in g.triples((o, None, None)):
            yield s2, p2, o2
            print(f"\t\tneighbor of neighbor: {o2}")


def main():
    g = Graph()

    print("Loading " + str(UBY) + " ...")
    start = time.time()
    g = g.parse(location=str(UBY), format="nt")
    print("Graph loaded in " + str(time.time() - start) + "s.")

    with open(Path(PROJECT, "token_entries.txt")) as fd:
        token_ids = fd.readlines()

    token_graph = Graph()
    for token_id in token_ids:
        for neighbor in get_neighbors(g, token_id):
            token_graph.add(neighbor)

    export_results(token_graph)


if __name__ == "__main__":
    main()
