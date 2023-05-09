#!/bin/bash
python3 ledger.py "$@" --price-db prices_db \
-f index.ledger
