#!/usr/bin/env python
import sys
from factsens.data import load_items
for p in sys.argv[1:]:
    print(p, len(load_items(p)), "items OK")
