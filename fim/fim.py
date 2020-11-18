#!/usr/bin/env python3
import pickle
import time

from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, NamespaceManager
from rdflib.term import Node

PROJECT_ROOT = Path("/home/orang3/code/Thesis")

TWEETS_DIR = Path(PROJECT_ROOT, "tweet-extraction")
TWEETS = Path(TWEETS_DIR, "first_10M_lines.n3")

GENERATED = Path(PROJECT_ROOT, "fim", "generated")
if not GENERATED.is_dir():
    GENERATED.mkdir(parents=True, exist_ok=True)

UBY_DIR = Path(PROJECT_ROOT, "UBY")
UBY_NEIGHBORS = Path(UBY_DIR, "uby-neighbors.nt")

SCHEMA = Namespace("http://schema.org/")
NEE = Namespace("http://www.ics.forth.gr/isl/oae/core#")
SIOC = Namespace("http://rdfs.org/sioc/ns#")
LEMON = Namespace("http://www.monnet-project.eu/lemon#")

g = Graph()
for prefix in [("lemon", LEMON),
               ("nee", NEE),
               ("rdf", RDF),
               ("schema", SCHEMA),
               ("sioc", SIOC)]:
    g.bind(*prefix)


for kb, fmt in [(TWEETS, "n3"), (UBY_NEIGHBORS, "nt")]:
    print("Loading " + str(kb) + "...")
    start = time.time()
    g.parse(location=str(kb), format=fmt)
    print(f"Graph loaded in {round((time.time() - start) / 60, ndigits=2)}m.")


def visit_tweet_graph(node, current_level=0, max_level=10, visited=defaultdict(bool)):
    for t in g.triples((node, None, None)):
        if not visited[t]:
            visited[t] = True
            yield t
        if current_level <= (max_level - 1):
            yield from visit_tweet_graph(t[2],
                                         current_level=(current_level + 1),
                                         visited=visited)


def tweetskb_triples(tweet_graph, entity, rep):
    tweet_graph.add((entity, NEE.detectedAs, rep))
    for uri in g.objects(entity, NEE.hasMatchedURI):
        tweet_graph.add((entity, NEE.hasMatchedURI, uri))
    return tweet_graph


def uby_triples(tweet_graph, rep):
    for canonical_form in g.subjects(LEMON.writtenRep, rep):
        tweet_graph.add((canonical_form, LEMON.writtenRep, rep))
        for sense in g.subjects(LEMON.canonicalForm, canonical_form):
            tweet_graph.add((sense, LEMON.canonicalForm, canonical_form))
            for t in visit_tweet_graph(sense, max_level=3):
                tweet_graph.add(t)
    return tweet_graph


def token_neighbors(tweet_id, tweet_graph):
    for post in g.subjects(SIOC.id, Literal(tweet_id)):
        for entity in g.objects(post, SCHEMA.mentions):
            for rep in g.objects(entity, NEE.detectedAs):
                # FIXME: Think about tokenization
                for token in rep.split(" "):
                    tweet_graph = tweetskb_triples(tweet_graph, entity, token)
                    tweet_graph = uby_triples(tweet_graph, token)
    return tweet_graph


def bag_of_terms(tweet_graph):
    bag = list()
    for triple in tweet_graph.triples((None, None, None)):
        bag.append(triple[0])
        bag.append(triple[2])
    return bag


def bag_of_triples(tweet_graph):
    return tuple(triple for triple in tweet_graph.triples((None, None, None)))


def get_tweets(paths):
    for tweet in paths:
        tweet_graph = Graph()
        tweet_id = str(tweet.name)[1:][:-3]

        # Add TOKEN related triples.
        tweet_graph = token_neighbors(tweet_id, tweet_graph)
        # Add DBPEDIA entities triples.
        tweet_graph.parse(location=str(tweet), format="nt")

        tweet_graph.serialize(destination=str(Path(GENERATED, f"t{tweet_id}.ttl")), format="turtle")

        yield tweet_graph


def build_db(bags):
    print("Building transaction database...")
    start = time.time()
    bags = list(bags)

    print("Building columns...")
    columns = np.array(list(set(item
                                for bag in bags
                                for item in bag)),
                       dtype=Node)

    print("Building rows...")
    rows = np.array(list([float(c in b) for c in columns]
                         for b in bags),
                    dtype=np.float64)

    print(f"Built in {round((time.time() - start) / 60, ndigits=2)}m.")
    return columns, rows


# Support(B) = (Transactions containing (B))/(Total Transactions)
#
#
# Confidence refers to the likelihood that an item B is also bought if item A is bought
#
# Confidence(A→B) = (Transactions containing both (A and B))/(Transactions containing A)
#
#
# Lift(A -> B) refers to the increase in the ratio of sale of B when A is sold
#
# Lift(A→B) = (Confidence (A→B))/(Support (B))


def column_idx(column, columns):
    idx = np.where(np.all(columns == column, axis=1))[0]
    if idx.size:
        return idx[0]
    else:
        return None


def get_large_1_sets(rows, min_sup=1e-3):
    supports_selected = {}
    # Sum columns and divide by number of transactions
    supports = rows.sum(axis=0) / float(rows.shape[0])
    sets = []
    for i, sup in enumerate(supports):
        if sup >= min_sup:
            item = frozenset([i])
            supports_selected[item] = sup
            sets.append(item)
    return frozenset(sets), supports_selected


# http://ethen8181.github.io/machine-learning/association_rule/apriori.html
# https://medium.com/cracking-the-data-science-interview/an-introduction-to-big-data-itemset-mining-a97a17e0665a

def candidate_itemsets(last_l, k):
    ck = set()
    for f1, f2 in combinations(set(item for item in last_l), 2):
        if k == 1:
            ck.add(frozenset(f1 | f2))
        else:
            # if the two (k)-item sets has
            # k - 1 common elements then they will be
            # unioned to be the (k+1)-item candidate
            intersection = f1 & f2
            if len(intersection) == k - 1:
                item = f1 | f2
                if item not in ck:
                    print(f"Selected {item}...")
                    ck.add(frozenset(item))
    return frozenset(ck)


def select_rows(candidate, rows):
    if np.all(rows[:, tuple(candidate)] == 1.0):
        return rows

    selected = np.ones(rows.shape[0], dtype=bool)
    for col in candidate:
        selected = selected & (rows[:, col] == 1.0)
        if not np.any(selected):
            return np.array([])

    return rows[selected, :]


def item_to_string(item):
    return "{" + ', '.join(map(str, item)) + "}"


def frequent_itemsets(rows, min_sup=0.027, max_length=5):
    if min_sup <= 0:
        raise ValueError('minimum support must be > 0')

    l1, supports = get_large_1_sets(rows)
    k = 1
    last_l = l1
    lk = l1

    while len(lk) > 0 and k <= max_length:
        k = len(next(iter(lk)))
        ck = candidate_itemsets(lk, k)
        ck_len = len(ck)
        lk = set()

        # Select candidates
        for i, candidate in enumerate(ck):
            print(f"Computing {item_to_string(candidate)} support...\t[{i + 1}/{ck_len}]")
            # Get rows which contain the candidate set
            selected = select_rows(candidate, rows)

            # Compute support of the candidate set
            support = selected.shape[0] / float(rows.shape[0])
            supports[candidate] = support

            if np.greater_equal(support, min_sup):
                lk.add(candidate)

        last_l = last_l | lk

        with open(f"last_{k + 1}.pickle", "wb") as fp:
            pickle.dump(last_l, fp)

        if ck_len > 0:
            print(f"Selected {len(lk)}/{ck_len} candidates i.e. the "
                  f"{round((len(lk) / float(ck_len)) * 100.0, ndigits=2)}% of them.")

    items = [[] for _ in range(k)]

    for el in last_l:
        items[len(el) - 1].append(el)

    return items, supports


def create_rules(freq_items, min_confidence):
    """
    create the association rules, the rules will be a list.
    each element is a tuple of size 4, containing rules,
    left hand side, right hand side, confidence and lift
    """
    association_rules = []

    # for the list that stores the frequent items, loop through
    # the second element to the one before the last to generate the rules
    # because the last one will be an empty list. It's the stopping criteria
    # for the frequent itemset generating process and the first one are all
    # single element frequent itemset, which can't perform the set
    # operation X -> Y - X
    for idx, freq_item in enumerate(freq_items[1:(len(freq_items) - 1)]):
        for freq_set in freq_item:

            # start with creating rules for single item on
            # the right hand side
            subsets = [frozenset([item]) for item in freq_set]
            rules, right_hand_side = compute_conf(supports, freq_set, subsets, min_confidence)
            association_rules.extend(rules)

            # starting from 3-itemset, loop through each length item
            # to create the rules, as for the while loop condition,
            # e.g. suppose you start with a 3-itemset {2, 3, 5} then the
            # while loop condition will stop when the right hand side's
            # item is of length 2, e.g. [ {2, 3}, {3, 5} ], since this
            # will be merged into 3 itemset, making the left hand side
            # null when computing the confidence
            if idx != 0:
                k = 1
                while len(right_hand_side[0]) < len(freq_set) - 1:
                    ck = candidate_itemsets(right_hand_side, k)
                    rules, right_hand_side = compute_conf(supports, freq_set, ck, min_confidence)
                    association_rules.extend(rules)
                    k += 1

    return association_rules


def compute_conf(supports, freq_set, subsets, min_confidence):
    """
    create the rules and returns the rules info and the rules's
    right hand side (used for generating the next round of rules)
    if it surpasses the minimum confidence threshold
    """
    rules = []
    right_hand_side = []

    for rhs in subsets:
        # create the left hand side of the rule
        # and add the rules if it's greater than
        # the confidence threshold
        lhs = freq_set - rhs
        conf = supports[freq_set] / supports[lhs]
        if conf >= min_confidence:
            lift = conf / supports[rhs]
            rules_info = lhs, rhs, conf, lift
            rules.append(rules_info)
            right_hand_side.append(rhs)

    return rules, right_hand_side


if __name__ == "__main__":
    # get itemsets
    tweets = get_tweets(Path(TWEETS_DIR, "related", "relations").iterdir())
    bags = map(bag_of_terms, tweets)

    columns, rows = build_db(bags)

    np.save("rows", rows)
    np.save("columns", columns, allow_pickle=True)

    columns = np.load("columns.npy", allow_pickle=True)
    rows = np.load("rows.npy")

    last_l, supports = frequent_itemsets(rows)

    with open("last.pickle", "wb") as fp:
        pickle.dump(last_l, fp)

    with open("supports.pickle", "wb") as fp:
        pickle.dump(supports, fp)

    with open("last.pickle", "rb") as fp:
        last_l = pickle.load(fp)
    with open("supports.pickle", "rb") as fp:
        supports = pickle.load(fp)

    rules = create_rules(last_l, min_confidence=0.01)
    with open("rules.pickle", "wb") as fp:
        pickle.dump(rules, fp)

    join_urls = lambda urls: "\n".join(columns[i] for i in urls)
    for lhs, rhs, conf, lift in sorted(rules, key=lambda info: info[3]):
        print("---------------------------------------------------------")
        left = join_urls(lhs)
        right = join_urls(rhs)
        msg = f"{left}\n\n=>\n\n{right}\n\nwith confidence {conf} and lift {lift}"
        print(msg)
        print("---------------------------------------------------------")
