#!/bin/sh
COMMENT=$1; shift
git config --local user.name "$GITHUB_ACTOR"
git config --local user.email "$GITHUB_ACTOR@bots.github.com"
git add -v "${@}"
git commit -m "$COMMENT" -a || exit 0
git pull
git push --force
