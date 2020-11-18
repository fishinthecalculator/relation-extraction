#!/usr/bin/env python3

import sys
import time

from pathlib import Path

from rdflib import Graph, URIRef, Literal

PROJECT = Path("/home/orang3/code/Thesis/UBY")
UBY = Path(PROJECT, "vn.nt")

g = Graph()

print("Loading " + str(UBY) + " ...")
start = time.time()
g = g.parse(location=str(UBY), format="nt")
print("Graph loaded in " + str(time.time() - start) + "s.")

written_rep = URIRef("http://www.monnet-project.eu/lemon#writtenRep")


def lookup_rep(rep, rep_graph):
    rep = Literal(rep)
    for sub in g.subjects(written_rep, rep):
        rep_graph.add((sub, written_rep, rep))


if __name__ == "__main__":
    rep_graph = Graph()
    if not sys.stdin.isatty():
        for line in sys.stdin:
            line = line.strip()
            if line:
                lookup_rep(line, rep_graph)
        print(rep_graph.serialize(format="nt").decode("utf-8"))
