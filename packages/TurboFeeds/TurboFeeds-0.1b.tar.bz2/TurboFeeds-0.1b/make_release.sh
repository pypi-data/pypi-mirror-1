#!/bin/sh

# make_release.sh - automates steps to build a TurboFeeds release

if [ "x$1" = "x-f" ]; then
    FINAL=yes
fi

SVN_BASE_URL="svn+ssh://svn/coding"
VERSION=$(python -c 'from turbofeeds.release import version;print version')
PROJECT_NAME=$(python -c 'from turbofeeds.release import name;print name')
HOMEPAGE=$(python -c 'from turbofeeds.release import url;print url')

RST2HTML_OPTS='--stylesheet-path=rest.css --link-stylesheet --input-encoding=UTF-8 --output-encoding=UTF-8 --language=en --no-xml-declaration'

# clean up
find . -name "*.pyc" -o -name "*.pyo" | xargs rm -f
rm -rf build doc/api doc/index.html README.txt*

# create README form template
cheetah fill --iext .in --oext .txt --odir . README.in
test $? -eq 0 || exit 1

# convert ReST to HTML
RST2HTML=$(which rst2html 2>/dev/null)
if [ -z "$RST2HTML" ]; then
    RST2HTML=$(which rst2html.py 2>/dev/null)
fi
mkdir -p doc
( cd doc; \
  "$RST2HTML" $RST2HTML_OPTS --date --time ../README.txt >index.html; )


# generate API documentation
( cd doc; \
  epydoc --html --url "$HOMEPAGE" --name $PROJECT_NAME \
  --output=api --no-frames -v ../turbofeeds; )

# Build distribution packages
if [ "x$FINAL" != "xyes" ]; then
    python setup.py sdist --formats=zip,bztar
    python setup.py bdist_egg
else
    # Check if everything is commited
    SVN_STATUS=$(svn status)
    if [ -n "$SVN_STATUS" ]; then
        echo "SVN is not up to date. Please fix." 2>&1
        exit 1
    fi

    # tag release in SVN
    echo svn copy "$SVN_BASE_URL/$PROJECT_NAME/trunk" \
      "$SVN_BASE_URL/$PROJECT_NAME/tags/$VERSION" -m "Tagging release $VERSION"
    # and upload & register them at the Cheeseshop if "-f" option is given 
    python setup.py register
    python setup.py sdist --formats=zip,bztar upload
    python setup.py bdist_egg upload
    # update web site
    ./upload.sh
fi
