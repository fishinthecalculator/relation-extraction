import pickle
import numpy as np

from argparse import ArgumentParser
from pathlib import Path


def parse_sorting_criteria(criterium):
    if criterium == "lift":
        return 3
    elif criterium == "allconf":
        return 4
    elif criterium == "coherence":
        return 5
    elif criterium == "cosine":
        return 6
    elif criterium == "kulc":
        return 7
    elif criterium == "maxconf":
        return 8
    else:
        raise ValueError(f"The provided sorting criterium '{criterium}' does not exist.")


def main(args):
    columns = np.load(args.columns,
                      allow_pickle=True)

    with open(args.rules, "rb") as fp:
        rules = pickle.load(fp)

    join_urls = lambda urls: "\n".join(columns[i] for i in urls)
    criterium = parse_sorting_criteria(args.sort_by)
    for lhs, rhs, conf, lift, ac, coh, cos, kulc, mc in sorted(rules, key=lambda info: info[criterium]):
        print("---------------------------------------------------------")
        left = join_urls(lhs)
        right = join_urls(rhs)

        msg = f"{left}\n\n=>\n\n{right}\n\nwith\n"
        msg += f"\tConfidence: {conf}\n"
        msg += f"\tLift: {lift}\n"
        msg += f"\tAllConf: {ac}\n"
        msg += f"\tCoherence: {coh}\n"
        msg += f"\tCosine: {cos}\n"
        msg += f"\tKulc: {kulc}\n"
        msg += f"\tMaxConf: {mc}\n"

        print(msg + "---------------------------------------------------------")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-c", "--columns", type=Path, required=True,
                        help="Path to the transaction's database in .npy format.")
    parser.add_argument("-r", "--rules", type=Path, required=True,
                        help="Path to the generated rules .pickle serialization.")
    parser.add_argument("-s", "--sort-by", type=str, required=True, default="lift",
                        help=".",
                        choices={"allconf",
                                 "coherence",
                                 "cosine",
                                 "kulc",
                                 "maxconf",
                                 "lift"})

    args = parser.parse_args()

    main(args)
