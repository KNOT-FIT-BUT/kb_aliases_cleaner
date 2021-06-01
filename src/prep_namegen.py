#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io

POS_NAME = 2
POS_SRC = 0
POS_GENDER = 1

with io.open("num_aliases.tsv", "r", encoding="utf8") as n:
    lines = n.readlines()

with io.open("namegen_input.txt", "w", encoding="utf8") as ni:
    for line in lines:
        line = line.split("\t")
        # saves name in format source_name \t\t P::GENDER \t
        ni.write(
            line[POS_NAME].split("#")[POS_SRC]
            + "\t\t"
            + "P:::"
            + line[POS_NAME].split("#")[POS_GENDER]
            + "\n"
        )
