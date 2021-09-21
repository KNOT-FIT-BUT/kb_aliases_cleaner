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

from src.destroy_alias import TARGETS, GN_NAMES, POS_ALIAS
from src.kb import add_tool_version, get_kb_toc


FLAGS_SEPARATOR = "#"
FLAG_ALIAS_DELETED = "mark=deleted"


def mark_aliases(arr, targets):
    for i in range(len(arr)):
        alias_with_flags = arr[i].split(FLAGS_SEPARATOR)
        if alias_with_flags[0] in targets:
            if FLAG_ALIAS_DELETED not in alias_with_flags[1:]:
                arr[i] = arr[i] + f"{FLAGS_SEPARATOR}{FLAG_ALIAS_DELETED}"
    return arr


if __name__ == "__main__":
    match_dict = dict()
    alias_dict = dict()

    THRESHOLD = 2
    DEBUG = False
    DESTROY = False
    KB_PATH = "./KB.tsv"
    OUTPUT_PATH = "./KB.tsv"

    args = sys.argv[1:]
    lopts = ["destroy", "debug", "input-file=", "output-file="]
    optlist, args = getopt.getopt(args, "hdt:", lopts)
    ROOTDIR = os.path.dirname(os.path.realpath(__file__))

    for option, value in optlist:
        if option == "-h":
            print("./filter_alias [options]")
            print("\t-h\t- Shows help")
            print(
                f"\t-t\t- Expects you to provide new THRESHOLD value (implicitly {THRESHOLD})"
            )
            print("\t--destroy\t- Destructable mode")
            print("\t--debug\t- Debug mode")
            print(
                f"\t--input-file\t- Expects you to provide path to input KB (implicitly {KB_PATH})"
            )
            print(
                f"\t--output-file\t- Expects you to provide path to output KB (implicitly {OUTPUT_PATH})"
            )
            exit()
        elif option == "--debug":
            DEBUG = True
        elif option == "--destroy":
            DESTROY = True
        elif option == "-t":
            THRESHOLD = int(value)
        elif option == "--input-file":
            KB_PATH = value
        elif option == "--output-file":
            OUTPUT_PATH = value
        else:
            assert False

    match_alias.find_problematic_aliases(KB_PATH, alias_dict)

    aliases = set(alias_dict.keys())
    aliases_to_remove = match_alias.find_odd_aliases(aliases)
    aliases.symmetric_difference_update(aliases_to_remove)

    match_alias.match_aliases(KB_PATH, aliases, alias_dict, match_dict)
    match_alias.remove_useless_matches(alias_dict, match_dict, THRESHOLD)

    if DEBUG == True:
        match_alias.write_numbered_aliases("num_aliases.tsv", alias_dict)
        match_alias.write_matches("aliases_match.tsv", match_dict)
        match_alias.write_aliases("aliases.txt", alias_dict)

    # Using namegen to determinate targets
    print("[*] Starting prep_namegen.py")
    print("[*] Generating temporal files")
    subprocess.call(["python3", f"{ROOTDIR}/src/prep_namegen.py"])
    print("[*] Starting namegen and generating names")
    FNULL = open(os.devnull, "w")
    subprocess.call(
        [
            "python3",
            f"{ROOTDIR}/namegen/namegen.py",
            "-gn",
            "namegen_gn_output.txt",
            "namegen_input.txt",
        ],
        stdout=FNULL,
        stderr=subprocess.STDOUT,
    )

    given_names = destroy_alias.get_items("namegen_gn_output.txt", GN_NAMES)
    targets = destroy_alias.get_items(None, TARGETS, target_dict=alias_dict)

    print("[*] Generating temporal files")
    os.remove("namegen_input.txt")
    os.remove("namegen_gn_output.txt")
    targets.intersection_update(given_names)

    with open(KB_PATH, "r") as KB:
        KB_lines = KB.readlines()

    KB = open(OUTPUT_PATH, "w")

    _, _, toc_kb_tools_versions, _, toc_kb_data = get_kb_toc(kb_content=KB_lines)
    if toc_kb_tools_versions:
        tools_versions = json.loads(KB_lines[toc_kb_tools_versions])
        add_tool_version(
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
        if DESTROY == True:
            aliases = filter(
                lambda name: not (name.split(FLAGS_SEPARATOR)[0] in targets), aliases
            )
        else:
            aliases = mark_aliases(aliases, targets)
        line[POS_ALIAS] = "|".join(list(aliases))
        KB.write("\t".join(line))

    KB.close()
