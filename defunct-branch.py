#!/usr/bin/env python3
"""Replace a local Git branch with a defunct-* tag."""

from __future__ import annotations

import argparse
import subprocess
import sys


def git(*args: str) -> str:
    result = subprocess.run(
        ("git", *args), text=True, capture_output=True, check=False
    )
    if result.returncode:
        message = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(message)
    return result.stdout.strip()


def current_branch() -> str:
    branch = git("branch", "--show-current")
    if not branch:
        raise RuntimeError("not on a branch; provide a branch name explicitly")
    return branch


def branch_exists(branch: str) -> bool:
    result = subprocess.run(
        ("git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"),
        check=False,
    )
    return result.returncode == 0


def tag_exists(tag: str) -> bool:
    result = subprocess.run(
        ("git", "show-ref", "--verify", "--quiet", f"refs/tags/{tag}"),
        check=False,
    )
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replace a local branch with a defunct-* tag."
    )
    parser.add_argument("branch", nargs="?", help="branch to retire")
    args = parser.parse_args()

    try:
        branch = args.branch or current_branch()
        tag = f"defunct-{branch}"
        if not branch_exists(branch):
            raise RuntimeError(f"branch does not exist: {branch}")
        if tag_exists(tag):
            raise RuntimeError(f"tag already exists: {tag}")
        git("tag", tag, branch)
        if git("branch", "--show-current") == branch:
            git("switch", "--detach")
        git("branch", "-D", branch)
    except RuntimeError as error:
        print(f"defunct-branch: {error}", file=sys.stderr)
        return 1

    print(f"Replaced {branch} with {tag}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
