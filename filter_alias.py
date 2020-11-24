#!/usr/bin/env python3
# encoding: utf-8
"""
Alias filtering tool that works as subphase of generating the knowledge base.
It finds conflicting aliases (single worded), sorts them and filters them.

author: Daniel Kříž
contact: xkrizd03@fit.vutbr.cz
"""

import os
import sys
import getopt
import subprocess
import src.match_alias as match_alias
import src.destroy_alias as destroy_alias

from src.destroy_alias import TARGETS, GN_NAMES, POS_ALIAS
from src.match_alias import KB_HEAD

if __name__ == '__main__':
    match_dict = dict()
    alias_dict = dict()

    THRESHOLD = 2
    DEBUG = False
    KB_PATH = './KB.tsv'
    OUTPUT_PATH = './KB.tsv'

    args = sys.argv[1:]
    optlist, args = getopt.getopt(args, 'hdt:', ['input-file=', 'output-file='])

    for option, value in optlist:
        if option == '-h':
            print("./filter_alias [options]")
            print("\t-h\t- Shows help")
            print("\t-d\t- Debug mode")
            print("\t-t\t- Expects you to provide new THRESHOLD value (implicitly 2)")
            print("\t--input-file\t- Expects you to provide path to input KB (implicitly ./KB.all)")
            print("\t--output-file\t- Expects you to provide path to output KB (implicitly ./KB.all)")
            exit()
        elif option == '-d':
            DEBUG = True
        elif option == '-t':
            THRESHOLD = int(value)
        elif option == '--input-file':
            KB_PATH = value
        elif option == '--output-file':
            OUTPUT_PATH = value
        else:
            assert False

    match_alias.find_problematic_aliases(KB_PATH, alias_dict)

    aliases = set(alias_dict.keys())
    aliases_to_remove = match_alias.find_odd_aliases(aliases)
    aliases.symmetric_difference_update(aliases_to_remove)

    match_alias.match_aliases(KB_PATH, aliases, alias_dict, match_dict)
    match_alias.remove_useless_matches(alias_dict, match_dict, THRESHOLD)
    match_alias.write_numbered_aliases('num_aliases.tsv', alias_dict)

    if DEBUG == True:
        match_alias.write_matches('aliases_match.tsv', match_dict)
        match_alias.write_aliases('aliases.txt', alias_dict)

    # Using namegen to determinate targets
    print('[*] Starting prep_namegen.py')
    subprocess.call('./src/prep_namegen.py')
    print('[*] Starting namegen and generating names')
    FNULL = open(os.devnull, 'w')
    subprocess.call(['./namegen/namegen.py', '-gn', 'namegen_gn_output.txt',
                         'namegen_input.txt'], stdout=FNULL,
                         stderr=subprocess.STDOUT)

    targets = destroy_alias.get_items('num_aliases.tsv', TARGETS)
    given_names = destroy_alias.get_items('namegen_gn_output.txt',
                                          GN_NAMES)

    targets.intersection_update(given_names)

    with open(KB_PATH, 'r') as KB:
        KB_lines = KB.readlines()

    KB = open(OUTPUT_PATH, 'w')

    # insert KB HEAD to the rewriten KB
    for idx in range(KB_HEAD):
        KB.write(KB_lines[idx])

    for num in range(KB_HEAD, len(KB_lines)):
        line = KB_lines[num]
        line = line.split('\t')
        aliases = line[POS_ALIAS].split('|')
        aliases = filter(lambda name: not (name.split('#')[0] in targets),
                         aliases)
        line[POS_ALIAS] = '|'.join(list(aliases))
        KB.write('\t'.join(line))

    KB.close()
