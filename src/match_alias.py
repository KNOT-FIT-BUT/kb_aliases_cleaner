#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
match_alias.py contains functions and classes used to find problematic aliases
in knowledge base and provide corresponding output

author: Daniel Kříž
contact: xkrizd03@fit.vutbr.cz
"""

import sys
import kb

ALIAS_MATCH = 1
NUM_ALIAS = 2
NAME = "name"
LINE = "line"

KB_HEAD = kb.get_kb_head_positions()

POS_MATCH_LINE = 0
POS_TYPE = KB_HEAD["generic"]["type"]
POS_NAME = KB_HEAD["generic"]["name"]
POS_DIS_NAME = KB_HEAD["generic"]["disambiguation_name"]
POS_ALIAS = KB_HEAD["generic"]["aliases"]
POS_GENDER = KB_HEAD["person"]["gender"]

ODD_CHARACTERS = [".", ",", "/", "_", "\\", "|", "+", "*", "&", "%", "$"]


class Match:
    """ Class representing match of line with alias """

    def __init__(self, line=0, name=None, dis_name=None, matched_alias=None):
        self.line = line
        self.name = name
        self.dis_name = dis_name
        self.matched_alias = matched_alias

    def __str__(self):
        alias_entry = str(self.matched_alias)
        entry = "\t".join([str(self.line), self.name, self.dis_name, "//", alias_entry])
        return entry

    def increment_match_cnt(self):
        """ increments count of matched lines for matched alias """
        self.matched_alias.match_cnt += 1


class Alias:
    """ Class representing an alias found it KB """

    def __init__(self, alias=None, match=None):
        self.alias = alias
        self.match_lines = [str(match[LINE])]
        self.match_sources = [match[NAME]]
        self.match_cnt = 1

    def __str__(self):
        entry = str()
        entry = "\t".join(
            [self.alias, "|".join(self.match_lines), "|".join(self.match_sources)]
        )
        return entry

    def alias_in_line(self, line, match_dict):
        """ Checks whether an alias is in a line """
        self.match_cnt += 1
        try:
            match_dict[self.alias].append(
                Match(line[POS_MATCH_LINE], line[POS_NAME], line[POS_DIS_NAME], self)
            )
        except KeyError:
            match_dict[self.alias] = [
                Match(line[POS_MATCH_LINE], line[POS_NAME], line[POS_DIS_NAME], self)
            ]

    def group_alias(self, new_match=None):
        """ Groups different sources of the same alias together """
        self.match_lines.append(str(new_match[LINE]))
        self.match_sources.append(new_match[NAME])


def convert_line_to_set(line):
    """takes the line and extracts every word  that could be matched with an
    alias, returns set of these names (there are no duplicates)"""
    converted_line = line
    # we have to tread line[POS_ALIAS] differently due to the #lang suffix
    converted_line[POS_ALIAS] = "|".join(
        [alias.partition("#")[0] for alias in line[POS_ALIAS].split("|")]
    )
    converted_line = " ".join(converted_line)
    return set((" ".join(converted_line.split("|")).split()))


def match_aliases(filename, aliases, aliases_dict, match_dict):
    """Matches aliases with lines in KB, aliases and matches are then writen
    in corresponding dictionaries"""
    with open(filename) as knowledge_base:
        knowledge_base_content = knowledge_base.readlines()
        toc_kb_data = kb.get_toc_kb_data(kb_content=knowledge_base_content)
        for idx, line in enumerate(
            knowledge_base_content[toc_kb_data:], start=toc_kb_data + 1
        ):
            line = line.split("\t")
            line[POS_MATCH_LINE] = str(idx)
            if line[POS_TYPE] != "person":
                continue
            mutated_aliases = aliases
            converted_line = convert_line_to_set(line)
            mutated_aliases = aliases.intersection(converted_line)
            update_matches(mutated_aliases, line, aliases_dict, match_dict)


def find_odd_aliases(aliases):
    """ Finds all odd aliases in set of aliases and returns them """
    odd_aliases = set()
    for alias in aliases:
        if is_odd_alias(alias):
            odd_aliases.add(alias)
    return odd_aliases


def is_odd_alias(alias):
    """Check if alias contains odd character, is whitespace or is not a name
    in general"""
    if alias[0].islower() and ("al-" not in alias or "d'" not in alias):
        return True
    elif len(alias) == 1 or alias.isnumeric() or alias.isspace():
        return True
    elif contains_odd_character(alias):
        return True
    else:
        return False


def contains_odd_character(word):
    """ Checks if word contains one of odd characters """
    for letter in word:
        if letter in ODD_CHARACTERS:
            return True
    return False


def update_matches(aliases, line, aliases_dict, match_dict):
    """ Updates dictionary of matches """
    for alias in aliases:
        aliases_dict[alias].alias_in_line(line, match_dict)


def write_matches(filename, match_dict):
    """ Takes matches dictionary and writes corresponding info to the file """
    with open(filename, "w") as aliases_match:
        sorted_match_dict = {
            k: v
            for k, v in sorted(
                match_dict.items(), key=lambda item: len(item[1]), reverse=True
            )
        }
        for match_group in sorted_match_dict.values():
            for match in match_group:
                aliases_match.write(str(match) + "\n")


def write_aliases(filename, alias_dict):
    """ Takes aliases and writes them to a file """
    with open(filename, "w") as aliases_file:
        for alias in alias_dict.keys():
            aliases_file.write(alias + "\n")


def write_numbered_aliases(filename, alias_dict):
    """Takes aliases and writes them with numerical info and
    first source name to the file"""
    sorted_alias_dict = {
        k: v
        for k, v in sorted(
            alias_dict.items(), key=lambda item: item[1].match_cnt, reverse=True
        )
    }
    with open(filename, "w") as numbered_aliases:
        for key in sorted_alias_dict.keys():
            entry = "\t".join(
                [
                    key,
                    str(sorted_alias_dict[key].match_cnt),
                    sorted_alias_dict[key].match_sources[0],
                    "\n",
                ]
            )
            numbered_aliases.write(entry)


def extract_aliases(line):
    """ Extracts aliases from line, then splits them them and returns them """
    aliases = [alias.partition("#")[0] for alias in line[POS_ALIAS].split("|")]
    names = line[POS_NAME].split("|")
    dis_names = line[POS_DIS_NAME].split("|")
    for name in names:
        if name.isnumeric():
            continue
        if name not in aliases:
            aliases.append(name)
    for dis_name in dis_names:
        if dis_name.isnumeric():
            continue
        if dis_name not in aliases:
            aliases.append(dis_name)
    return aliases


def assign_aliases_to_dict(aliases, alias_dict, line):
    """Assignes aliases to the alias dictionary, if the entry already exists
    then the matches are only grouped, otherwise new Alias instance is
    created"""
    if not aliases:
        return
    match = {LINE: line[POS_MATCH_LINE], NAME: line[POS_NAME] + "#" + line[POS_GENDER]}
    for alias in aliases:
        try:
            alias_dict[alias].group_alias(match)
        except KeyError:
            alias_dict[alias] = Alias(alias, match)


def find_problematic_aliases(filename, alias_dict):
    """Finds aliases in filename, name is considered problematic, if it is
    only one word long"""
    with open(filename) as knowledge_base:
        knowledge_base_content = knowledge_base.readlines()
        toc_kb_data = kb.get_toc_kb_data(kb_content=knowledge_base_content)
        for idx, line in enumerate(
            knowledge_base_content[toc_kb_data:], start=toc_kb_data + 1
        ):
            line = line.split("\t")
            line[POS_MATCH_LINE] = str(idx)
            if line[POS_TYPE] != "person":
                continue
            aliases = extract_aliases(line)
            aliases = filter(lambda alias: len(alias.split()) == 1, aliases)
            assign_aliases_to_dict(aliases, alias_dict, line)


def remove_useless_matches(alias_dict, match_dict, threshold=2):
    """Removes useless aliases and corresponding matches, alias is considered
    useless if its match_cnt is below or equal to threshold (default=2)"""
    aliases_to_remove = set()
    for key in alias_dict.keys():
        if alias_dict[key].match_cnt <= threshold:
            aliases_to_remove.add(key)
    for key in aliases_to_remove:
        alias_dict.pop(key)
        try:
            match_dict.pop(key)
        except KeyError:
            continue


if __name__ == "__main__":
    match_dict = dict()
    alias_dict = dict()

    find_problematic_aliases("KB_all.tsv", alias_dict)

    aliases = set(alias_dict.keys())
    aliases_to_remove = find_odd_aliases(aliases)
    aliases.symmetric_difference_update(aliases_to_remove)

    match_aliases("KB_all.tsv", aliases, alias_dict, match_dict)
    # in only match_alias.py the threshold is unchanged
    remove_useless_matches(alias_dict, match_dict)
    write_numbered_aliases("num_aliases.tsv", alias_dict)
    if (len(sys.argv) != 1) and sys.argv[1] == "-d":
        write_matches("aliases_match.tsv", match_dict)
        write_aliases("aliases.txt", alias_dict)
