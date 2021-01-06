#!/usr/bin/env python3
import os
import pickle
import time
from argparse import ArgumentParser

from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, XSD, DC, NamespaceManager
from rdflib.term import Node

PROJECT_ROOT = Path(os.environ["HOME"], "code", "Thesis")

TWEET_EXTRACTION = Path("PROJECT_ROOT", "tweet-extraction")
TWEETS = Path(TWEET_EXTRACTION, "first_10M_lines.n3")
TWEETS_WITH_RELATIONS = Path(TWEET_EXTRACTION, "related")

FIM = Path(PROJECT_ROOT, "fim")
GRAPHS = Path(FIM, "generated")

UBY_DIR = Path(PROJECT_ROOT, "UBY")
UBY_NEIGHBORS = Path(UBY_DIR, "uby-neighbors.nt")

NEE = Namespace("http://www.ics.forth.gr/isl/oae/core#")
SCHEMA = Namespace("http://schema.org/")
SIOC = Namespace("http://rdfs.org/sioc/ns#")
SIOC_T = Namespace("http://rdfs.org/sioc/types#")
ONYX = Namespace("http://www.gsi.dit.upm.es/ontologies/onyx/ns#")
WNA = Namespace("http://www.gsi.dit.upm.es/ontologies/wnaffect/ns#")

LEMON = Namespace("http://www.monnet-project.eu/lemon#")
DBO = Namespace("http://dbpedia.org/ontology/")

g = Graph()


def load_graphs():
    merge_graph = Graph()
    for prefix in [("rdf", RDF),
                   ("rdfs", RDFS),
                   ("xsd", XSD),
                   ("dc", DC),
                   ("lemon", LEMON),
                   ("nee", NEE),
                   ("dbo", DBO),
                   ("schema", SCHEMA),
                   ("wna", WNA),
                   ("SIOC_T", SIOC_T),
                   ("onyx", ONYX),
                   ("sioc", SIOC)]:
        merge_graph.bind(*prefix)

    for kb, fmt in [(TWEETS, "n3")]:
        print("Loading " + str(kb) + "...")
        start = time.time()
        merge_graph.parse(location=str(kb), format=fmt)
        print(f"Graph loaded in {round((time.time() - start) / 60, ndigits=2)}m.")

    return merge_graph


def tweetskb_triples(tweet_graph, entity):
    for uri in g.objects(entity, NEE.hasMatchedURI):
        tweet_graph.add((entity, NEE.hasMatchedURI, uri))
    return tweet_graph


def token_neighbors(tweet_id, tweet_graph):
    for post in g.subjects(SIOC.id, Literal(tweet_id)):
        for entity in g.objects(post, SCHEMA.mentions):
            tweet_graph = tweetskb_triples(tweet_graph, entity)
            for rep in g.objects(entity, NEE.detectedAs):
                tweet_graph.add((entity, NEE.detectedAs, rep))
    return tweet_graph


def bag_of_terms(tweet_graph):
    bag = list()
    for triple in tweet_graph.triples((None, None, None)):
        bag.append(triple[0])
        bag.append(triple[1])
        bag.append(triple[2])
        bag.append(f"{triple[0]}_{triple[1]}_{triple[2]}")

        # BA :spouse :MA
        # bag { :BA, :spouse, :MA, ?v0-:spouse-:MA, .... }
        # the indices of the variable are progressive naturals


        bag.append(f"{triple[0]}_{triple[1]}_X")
        bag.append(f"X_{triple[1]}_{triple[2]}")

    return bag


def bag_of_triples(tweet_graph):
    return tuple(triple for triple in tweet_graph.triples((None, None, None)))


def get_tweets(paths):
    for tweet in paths:
        tweet_graph = Graph()
        tweet_id = str(tweet.name)[1:][:-4]

        # Add TOKEN related triples.
        tweet_graph = token_neighbors(tweet_id, tweet_graph)
        # Add DBPEDIA entities triples.
        tweet_graph.parse(location=str(tweet), format="ttl")
        # Add UBY triples
        uby_triples = Path(UBY_NEIGHBORS, f"t{tweet_id}.ttl")
        # Not all tweets can be linked to UBY
        if uby_triples.is_file():
            tweet_graph.parse(location=str(uby_triples), format="ttl")

        tweet_graph.serialize(destination=str(Path(GRAPHS, f"t{tweet_id}.ttl")), format="turtle")

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
    supports_selected = defaultdict(float)
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


def compute_support(candidate, rows):
    # Get rows which contain the candidate set
    selected = select_rows(candidate, rows)

    # Compute support of the candidate set, i.e. the frequency
    return selected.shape[0] / float(rows.shape[0])


def item_to_string(item):
    return "{" + ', '.join(map(str, item)) + "}"


def frequent_itemsets(rows, min_sup=0.027, max_length=5):
    if min_sup <= 0:
        raise ValueError('minimum support must be > 0')

    l1, supports = get_large_1_sets(rows)
    k = 1
    last_l = l1
    lk = l1

    while len(lk) > 0 and k + 1 <= max_length:
        k = len(next(iter(lk)))
        ck = candidate_itemsets(lk, k)
        ck_len = len(ck)
        lk = set()

        # Select candidates
        for i, candidate in enumerate(ck):
            print(f"Computing {item_to_string(candidate)} support...\t[{i + 1}/{ck_len}]")

            support = compute_support(candidate, rows)
            supports[candidate] = support

            if np.greater_equal(support, min_sup):
                lk.add(candidate)

        last_l = last_l | lk

        with open(Path(FIM, f"last_{k + 1}.pickle"), "wb") as fp:
            pickle.dump(last_l, fp)

        if ck_len > 0:
            print(f"Selected {len(lk)}/{ck_len} candidates i.e. the "
                  f"{round((len(lk) / float(ck_len)) * 100.0, ndigits=2)}% of them.")

    items = [[] for _ in range(k + 1)]

    for el in last_l:
        items[len(el) - 1].append(el)

    return items, supports


# Re-examination of interestingness measures
# in pattern mining: a unified framework
# Tianyi Wu · Yuguo Chen · Jiawei Han
def conditional_probability(supports, a, b):
    """
    Convert the support counts into conditional
    probabilities using the following equations:

    P(a|b) = sup(ab) / sup(b) = sup(ab) / ( sup(ab) + sup(not(a)b) )

    """
    a_and_b = a & b
    b_and_not_a = b - a_and_b
    assert b == b_and_not_a
    sup_ab = supports[a | b]
    sup_b = supports[b]
    if sup_ab == 0.0 or sup_b == 0.0:
        return 0.0
    else:
        return sup_ab / sup_b


def all_conf(supports, a, b):
    # P(a|b)
    p_a_b = conditional_probability(supports, a, b)
    # P(b|a)
    p_b_a = conditional_probability(supports, b, a)
    return min(p_a_b, p_b_a)


def coherence(supports, a, b):
    # P(a|b)
    p_a_b = conditional_probability(supports, a, b)
    # P(b|a)
    p_b_a = conditional_probability(supports, b, a)
    return 1.0 / ((1.0 / p_a_b) + (1.0 / p_b_a) - 1)


def cosine(supports, a, b):
    # P(a|b)
    p_a_b = conditional_probability(supports, a, b)
    # P(b|a)
    p_b_a = conditional_probability(supports, b, a)
    return np.sqrt(p_a_b * p_b_a)


def kulc(supports, a, b):
    # P(a|b)
    p_a_b = conditional_probability(supports, a, b)
    # P(b|a)
    p_b_a = conditional_probability(supports, b, a)
    return (p_a_b + p_b_a) / 2.0


def max_conf(supports, a, b):
    # P(a|b)
    p_a_b = conditional_probability(supports, a, b)
    # P(b|a)
    p_b_a = conditional_probability(supports, b, a)
    return max(p_a_b, p_b_a)


# A transaction that does not contain an item i is called a null transaction with respect
# to (w.r.t.) item i.

# If a measure that assesses the association among a set of events
# being analyzed is affected by the number of transactions that contain none of them
# (i.e., null-transactions), such a measure is unlikely to be so interesting.

# Thus it is desirable to select a measure that is not influenced by
# the number of null transactions, i.e., null-invariant.

def compute_metrics(supports, freq_set, subsets, min_confidence):
    """
    create the rules and returns the rules info and the rules's
    right hand side (used for generating the next round of rules)
    if it surpasses the minimum confidence threshold
    """
    rules = []
    right_hand_side = []

    # we can constrain the rule gen search
    # {...} = > { ?v0 - dbo: spouse -?v1}

    # we can add prefixes to rules contents to figure out if a rule matches a pattern
    # bag = {term_: BA
    # tp =?v0 - dbo: spouse -?v1
    # {} = > {tp}

    for rhs in subsets:
        # create the left hand side of the rule
        # and add the rules if it's greater than
        # the confidence threshold
        lhs = freq_set - rhs
        conf = supports[freq_set] / supports[lhs]
        # if conf >= min_confidence:
        lift = conf / supports[rhs]
        rules_info = (lhs,
                      rhs,
                      conf,
                      lift,
                      all_conf(supports, lhs, rhs),
                      coherence(supports, lhs, rhs),
                      cosine(supports, lhs, rhs),
                      kulc(supports, lhs, rhs),
                      max_conf(supports, lhs, rhs))
        rules.append(rules_info)
        right_hand_side.append(rhs)

    return rules, right_hand_side


def create_rules(freq_items, supports, min_confidence):
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
            rules, right_hand_side = compute_metrics(supports, freq_set, subsets, min_confidence)
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
                    rules, right_hand_side = compute_metrics(supports, freq_set, ck, min_confidence)
                    association_rules.extend(rules)
                    k += 1

    return association_rules


def main():
    rows_npy_path = Path(FIM, "rows.npy")
    last_l_pickle = Path(FIM, "last.pickle")
    supports_pickle = Path(FIM, "supports.pickle")
    rules_pickle_path = Path(FIM, "rules.pickle")

    if not rows_npy_path.is_file():
        tweets = get_tweets(Path(TWEETS_WITH_RELATIONS).iterdir())
        bags = map(bag_of_terms, tweets)
        columns, rows = build_db(bags)

        np.save(Path(FIM, "rows"), rows)
        np.save(Path(FIM, "columns"), columns, allow_pickle=True)

    if (not last_l_pickle.is_file()) or (not supports_pickle.is_file()):
        rows = np.load(rows_npy_path)

        last_l, supports = frequent_itemsets(rows)

        with open(last_l_pickle, "wb") as fp:
            pickle.dump(last_l, fp)

        with open(supports_pickle, "wb") as fp:
            pickle.dump(supports, fp)

    if not rules_pickle_path.is_file():
        with open(last_l_pickle, "rb") as fp:
            last_l = pickle.load(fp)
        with open(supports_pickle, "rb") as fp:
            supports = pickle.load(fp)

        rules = create_rules(last_l, supports, min_confidence=0.01)
        with open(rules_pickle_path, "wb") as fp:
            pickle.dump(rules, fp)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-t", "--tweets-graph", type=Path, required=True,
                        help="Path of the TweetsKB graph representing the tweets and entities.")
    parser.add_argument("-r", "--related", type=Path, required=True,
                        help="Path of directory the graphs of the tweets that have at least one relationship between "
                             "their entities.")
    parser.add_argument("-u", "--uby-neighbors", type=Path, required=True,
                        help="Path of the graphs of the neighbors of all the tokens in a tweet.")
    parser.add_argument("-o", "--out-dir", type=Path, required=True,
                        help="Directory where the Turtle graphs of all the tweets that contain one or more "
                             "relationships will be exported.")

    args = parser.parse_args()
    FIM = args.out_dir
    GRAPHS = Path(FIM, "graphs")
    UBY_NEIGHBORS = args.uby_neighbors
    TWEETS = args.tweets_graph
    TWEETS_WITH_RELATIONS = args.related

    print(f"Output will be generated at {FIM}")

    g = load_graphs()

    main()
