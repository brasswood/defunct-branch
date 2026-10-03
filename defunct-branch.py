#!/usr/bin/env python3
"""Replace a local Git branch with a tag."""

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


def check_remote_up_to_date(branch: str) -> tuple[str, str]:
    upstream = git("rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}")
    if "/" not in upstream:
        raise RuntimeError(f"cannot determine remote branch for {branch}: {upstream}")
    remote, remote_branch = upstream.split("/", 1)
    git("fetch", remote)
    upstream = git("rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}")
    counts = git("rev-list", "--left-right", "--count", f"{branch}...{upstream}")
    ahead, behind = (int(count) for count in counts.split())
    if ahead or behind:
        raise RuntimeError(
            f"branch {branch} is not up to date with {upstream} "
            f"(ahead {ahead}, behind {behind}); refusing to retire it"
        )
    return remote, remote_branch


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replace a local branch with a defunct-* tag."
    )
    parser.add_argument("branch", nargs="?", help="branch to retire")
    parser.add_argument(
        "--keep-name",
        action="store_true",
        help="use the branch name as the tag name instead of adding defunct-",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="fetch and require an up-to-date upstream, then retire it remotely too",
    )
    args = parser.parse_args()

    try:
        branch = args.branch or current_branch()
        tag = branch if args.keep_name else f"defunct-{branch}"
        if not branch_exists(branch):
            raise RuntimeError(f"branch does not exist: {branch}")
        if tag_exists(tag):
            raise RuntimeError(f"tag already exists: {tag}")
        remote_info = check_remote_up_to_date(branch) if args.push else None
        git("tag", tag, branch)
        if remote_info is not None:
            remote, remote_branch = remote_info
            git("push", remote, "refs/tags/" + tag)
            git("push", remote, "--delete", remote_branch)
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
