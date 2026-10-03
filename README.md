# defunct-branch

Turn a local Git branch into a `defunct-` tag and remove the branch.

## Usage

From the repository containing the branch, run:

```console
defunct-branch.py [--keep-name] [--push] [BRANCH]
```

Without `BRANCH`, the script uses the currently checked-out branch. For
example, running `defunct-branch branchname` creates `defunct-branchname` at
the branch's tip, then deletes `branchname` locally.

Pass `--keep-name` to use the branch's name unchanged for the tag. For example,
`defunct-branch --keep-name release-1` replaces the `release-1` branch with a
`release-1` tag. Without this option, the `defunct-` prefix remains the default.

The script refuses to overwrite an existing tag. When retiring the checked-out
branch, it leaves Git detached at the branch's last commit. By default it makes
only local changes.

Pass `--push` to fetch the branch's configured upstream and require the local
branch to match it exactly. If either side has commits the other does not, the
script aborts without retiring the branch. On a match, it pushes the retirement
tag and deletes the upstream branch, then performs the local operations.
`--push` requires the branch to have a configured upstream.

## License

This project is dedicated to the public domain under CC0 1.0 Universal. See
[LICENSE](LICENSE) for the official legal code.
