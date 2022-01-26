#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
destroy_alias.py is a small tool, that filters aliases from KB depending on
num_aliases.tsv generated by match_alias,py tool and namegen output that
provides given names to be filtered.

@author: Daniel Kříž
@contact: xkrizd03@fit.vutbr.cz
"""

from kb import get_toc_kb_data

POS_ALIAS = 4
TARGETS = 0
GN_NAMES = 0


def get_items(filename, column, separator="\t", target_dict=None):
    """Returns word located in columb of a file defined as filename. Each
    line is separated with separator (default value = '\t')"""
    items = set()
    if not target_dict:
        with open(filename, "r") as opened_file:
            file_content = opened_file.readlines()
        for line in file_content:
            items.add(line.split(separator)[column])
    else:
        for key in target_dict:
            item = (key, target_dict[key].match_cnt, target_dict[key].match_sources[0])
            items.add(item[column])
    return items


if __name__ == "__main__":
    """This main entrypoint shows example usage of this module, to get
    data from file/dictionary and how to filter them from the KB"""

    targets = get_items("num_aliases.tsv", TARGETS)
    given_names = get_items("namegen_gn_output.txt", GN_NAMES, "\n")

    targets.intersection_update(given_names)

    with open("KB_all.tsv", "r") as KB:
        KB_lines = KB.readlines()

    KB = open("KB_all.tsv", "w")

    toc_kb_data = get_toc_kb_data(kb_content=KB_lines)
    # insert KB HEAD to the rewritten KB
    for idx in range(toc_kb_data):
        KB.write(KB_lines[idx])

    for num in range(toc_kb_data, len(KB_lines)):
        line = KB_lines[num]
        line = line.split("\t")
        aliases = line[POS_ALIAS].split("|")
        aliases = filter(lambda name: not (name.split("#")[0] in targets), aliases)
        line[POS_ALIAS] = "|".join(list(aliases))
        KB.write("\t".join(line))

    KB.close()
