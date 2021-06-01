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

from shlex import split as shlex_split


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
