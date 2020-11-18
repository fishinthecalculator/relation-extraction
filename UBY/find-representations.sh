#!/usr/bin/env bash

set -euo pipefail

../entities-literals.sh | python search-tokens.py
