#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tools for simplified manipulation with KB

@author: Tomáš Volf
@contact: ivolf@fit.vut.cz
"""

import json
import subprocess
import sys
import re

from shlex import split as shlex_split


GENERIC_REGEX = re.compile('^<__generic__>')
PERSON_REGEX = re.compile('^<person>')
GROUP_REGEX = re.compile('^<group>')
ARTIST_REGEX = re.compile('^<artist>')
GEOGRAPHICAL_REGEX = re.compile('^<geographical>')
EVENT_REGEX = re.compile('^<event>')
ORGANIZATION_REGEX = re.compile('^<organization>')
STATS_REGEX = re.compile('^<__stats__>')
TOC_KB_HEAD_POS = 3


def get_kb_toc(kb_content: list) -> [int, int, int, int, int]:
    toc_kb_version = 0
    toc_kb_head = None
    try:
        json.loads(kb_content[1])
        json.loads(kb_content[2])
        toc_kb_resources_versions = 1
        toc_kb_tools_versions = 2
    except json.decoder.JSONDecodeError:
        toc_kb_resources_versions = toc_kb_tools_versions = None
    except IndexError as e:
        sys.exit("Too short KB content.")

    for idx, line in enumerate(kb_content):
        if line == "\n":
            if toc_kb_resources_versions and toc_kb_tools_versions:
                if toc_kb_head:
                    toc_kb_data = idx + 1
                    break
                else:
                    toc_kb_head = idx + 1
            else:
                toc_kb_head = 1
                toc_kb_data = idx + 1
                break
    return [
        toc_kb_version,
        toc_kb_resources_versions,
        toc_kb_tools_versions,
        toc_kb_head,
        toc_kb_data,
    ]


def get_toc_kb_data(kb_content: list) -> int:
    _, _, _, _, toc_kb_data = get_kb_toc(kb_content=kb_content)
    return toc_kb_data


def get_kb_file_toc(kb_file: str) -> [int, int, int, int, int]:
    with open(kb_file) as f:
        return get_kb_toc(kb_content=f.readlines())


def add_tool_version(repo_dir: str, tools_versions: dict) -> None:
    try:
        repo_name = (
            subprocess.check_output(
                "basename `git config --get remote.origin.url`",
                cwd=repo_dir,
                shell=True,
            )
            .decode()
            .strip()
            .rstrip(".git")
        )
    except subprocess.CalledProcessError as err:
        sys.exit(f"Version capture failed - probably not a git repository ({repo_dir})")
    tools_versions[repo_name] = (
        subprocess.check_output(shlex_split("git rev-parse --short HEAD"), cwd=repo_dir)
        .decode()
        .strip()
    )
    if (
        subprocess.check_output(shlex_split("git status --short"), cwd=repo_dir)
        .decode()
        .strip()
    ):
        tools_versions[repo_name] += "_dirty"


def process_kb_head_line(line, data_dict, category, start_count=0) -> int:
    for idx, elem in enumerate(line, start_count):
        if elem.partition('>')[2]:
            elem = elem.partition('>')[2]
        if elem.partition('}')[2]:
            elem = elem.partition('}')[2]
        try:
            data_dict[category][elem.replace(' ', '_').lower()] = idx
        except KeyError:
            data_dict[category] = {}
            data_dict[category][elem.replace(' ', '_').lower()] = idx
    return len(line)


def get_kb_head_positions(kb_filename='KB.tsv'):
    with open(kb_filename) as kb_file:
        kb_header = {}
        generic_type_len: int = 0
        lines = kb_file.readlines()
        for line in lines[get_kb_toc(lines)[TOC_KB_HEAD_POS]:]:
            if not line.strip():
                break
            line = line.strip().split('\t')
            if GENERIC_REGEX.match(line[0]):
                generic_type_len = process_kb_head_line(line, kb_header, 'generic')
            elif PERSON_REGEX.match(line[0]):
                process_kb_head_line(line, kb_header, 'person', generic_type_len)
            elif GROUP_REGEX.match(line[0]):
                process_kb_head_line(line, kb_header, 'group', generic_type_len)
            elif ARTIST_REGEX.match(line[0]):
                process_kb_head_line(line, kb_header, 'artist', generic_type_len)
            elif GEOGRAPHICAL_REGEX.match(line[0]):
                process_kb_head_line(line, kb_header, 'geographical', generic_type_len)
            elif EVENT_REGEX.match(line[0]):
                process_kb_head_line(line, kb_header, 'event', generic_type_len)
            elif ORGANIZATION_REGEX.match(line[0]):
                process_kb_head_line(line, kb_header, 'organization', generic_type_len)
            elif STATS_REGEX.match(line[0]):
                process_kb_head_line(line, kb_header, 'stats', generic_type_len)
            else:
                raise('error: new kind of KB Type encountered, please update\
                      this script')
    return kb_header
