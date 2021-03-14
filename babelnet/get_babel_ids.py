import json
import pickle
import sys

import requests

service_url = 'https://babelnet.io/v5/getSynsetIds'

lang = 'EN'
key = "324b7843-45b3-4d9e-828d-144eaf684d79"
pos = "NOUN"

headers = {'Accept-encoding': 'gzip'}
ERROR = b'{"message":"Your key is not valid or the daily requests limit has been reached. Please visit http://babelnet.org."}\n'

synsets = {}
errors = set()


def export_and_exit(code=0):
    if code == 1:
        print("Error: REACHED API QUOTA!")
    with open("synsets.pickle", "wb") as fp:
        pickle.dump(synsets, fp)
    with open("synsets.json", "w") as fp:
        json.dump(synsets, fp, indent=2)
    sys.exit(code)


def query(lemma):
    params = {
        'lemma': lemma,
        'searchLang': lang,
        'pos': pos,
        'key': key
    }
    r = requests.get(service_url, params=params, headers=headers)
    if r.content == ERROR:
        export_and_exit(1)
    if r.status_code == requests.codes.ok:
        return r.json()


if __name__ == "__main__":
    with open("../single-words") as fp:
        lines = fp.readlines()

    for line in lines:
        lemma = line.strip()
        synsets[lemma] = query(lemma)

    export_and_exit()
