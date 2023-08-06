#!/bin/sh

BASE_DIR="/home/www/chrisarndt.de/htdocs/projects/"
HOST="chrisarndt.de"
USER="chris"

ssh "${USER}@${HOST}" mkdir -p "${BASE_DIR}/TurboFeeds"
rsync -v -r --update --exclude .svn doc/ "${USER}@${HOST}:${BASE_DIR}/TurboFeeds"
