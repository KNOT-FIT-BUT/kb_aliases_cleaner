#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alias filtering tool that works as subphase of generating the knowledge base.
It finds conflicting aliases (single worded), sorts them and filters them.

author: Daniel Kříž
contact: xkrizd03@fit.vutbr.cz
"""

import json
import os
import sys
import getopt
import subprocess
import src.match_alias as match_alias
import src.destroy_alias as destroy_alias
import kb

from src.destroy_alias import TARGETS, GN_NAMES, POS_ALIAS
from argparse import ArgumentParser


FLAGS_SEPARATOR = "#"
FLAG_ALIAS_DELETED = "mark=deleted"


def mark_aliases(arr, targets):
    """Marks the alias as deleted, for non-destructive run for the script"""
    for i in range(len(arr)):
        alias_with_flags = arr[i].split(FLAGS_SEPARATOR)
        if alias_with_flags[0] in targets:
            if FLAG_ALIAS_DELETED not in alias_with_flags[1:]:
                arr[i] = arr[i] + f"{FLAGS_SEPARATOR}{FLAG_ALIAS_DELETED}"
    return arr


if __name__ == "__main__":
    match_dict = dict()
    alias_dict = dict()
    ROOTDIR = os.path.dirname(os.path.realpath(__file__))

    parser = ArgumentParser(
        "filter_alias is a script that filters problematic aliases from the KB"
    )
    parser.add_argument(
        "--destroy",
        help="destructable mode, the aliases in input file will be erased, if"
        "there the output file is set, then this option will be ignored",
        action="store_true",
    )
    parser.add_argument(
        "--debug",
        help="debug mode, diagnostics files will be created",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--input-file",
        help="path to the input knowledge base",
        type=str,
        default="./KB.tsv",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        help="path to the output file",
        type=str,
        default="./KB.tsv",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        help="how many alias occurances are needed to mark alias as problematic",
        type=int,
        default=2,
    )
    args = vars(parser.parse_args())

    match_alias.find_problematic_aliases(args["output_file"], alias_dict)

    aliases = set(alias_dict.keys())
    aliases_to_remove = match_alias.find_odd_aliases(aliases)
    aliases.symmetric_difference_update(aliases_to_remove)

    match_alias.match_aliases(args["output_file"], aliases, alias_dict, match_dict)
    match_alias.remove_useless_matches(alias_dict, match_dict, args["threshold"])

    if args["debug"] == True:
        match_alias.write_numbered_aliases("num_aliases.tsv", alias_dict)
        match_alias.write_matches("aliases_match.tsv", match_dict)
        match_alias.write_aliases("aliases.txt", alias_dict)

    print("[*] Generating temporal input file for namegen")
    namegen_input = []
    for key in alias_dict:
        names = str(alias_dict[key]).split("\t")[2]
        for name in names.split("|"):
            name, gender = name.split("#")
            namegen_str = name + "\t\t" + "P:::" + gender + "\n"
            namegen_input.append(namegen_str)

    print("[*] Starting namegen and generating names")
    FNULL = open(os.devnull, "w")
    subprocess.run(
        [
            "python3",
            f"{ROOTDIR}/namegen/namegen.py",
            "-gn",
            "namegen_gn_output.txt",
        ],
        input="\n".join(namegen_input).encode("utf-8"),
        stdout=FNULL,
        stderr=subprocess.STDOUT,
    )

    given_names = destroy_alias.get_items("namegen_gn_output.txt", GN_NAMES)
    targets = destroy_alias.get_items(None, TARGETS, target_dict=alias_dict)

    print("[*] Removing temporal files")
    os.remove("namegen_gn_output.txt")

    targets.intersection_update(given_names)

    with open(args["input_file"], "r") as KB:
        KB_lines = KB.readlines()

    KB = open(args["output_file"], "w")

    _, _, toc_kb_tools_versions, _, toc_kb_data = kb.get_kb_toc(kb_content=KB_lines)
    if toc_kb_tools_versions:
        tools_versions = json.loads(KB_lines[toc_kb_tools_versions])
        kb.add_tool_version(
            repo_dir=os.path.dirname(os.path.realpath(__file__)),
            tools_versions=tools_versions,
        )
        KB_lines[toc_kb_tools_versions] = json.dumps(tools_versions) + "\n"

    # insert KB HEAD to the rewritten KB
    for idx in range(toc_kb_data):
        KB.write(KB_lines[idx])

    for num in range(toc_kb_data, len(KB_lines)):
        line = KB_lines[num]
        line = line.split("\t")
        aliases = line[POS_ALIAS].split("|")
        if args["destroy"] == True:
            aliases = filter(
                lambda name: not (name.split(FLAGS_SEPARATOR)[0] in targets), aliases
            )
        else:
            aliases = mark_aliases(aliases, targets)
        line[POS_ALIAS] = "|".join(list(aliases))
        KB.write("\t".join(line))

    KB.close()
