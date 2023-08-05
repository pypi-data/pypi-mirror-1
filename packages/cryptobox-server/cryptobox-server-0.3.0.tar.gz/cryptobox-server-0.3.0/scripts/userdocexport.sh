#!/bin/sh
#
#  Copyright (c) 02005 sense.lab <senselab@systemausfall.org>
#
#  License:  This script is distributed under the terms of version 2
#            of the GNU GPL. See the LICENSE file included with the package.
#
# $Id: userdocexport.sh 418 2006-09-06 13:13:17Z lars $
#
# export wiki pages to the cryptobox development tree
# this creates static and integrated pages
#

set -ue

# root directory of the cryptobox development environment
ROOT_DIR="$(dirname $0)/.."

# retrieve these pages from the wiki
PAGES="CryptoBox	CryptoBoxUser	CryptoBoxUserGettingStarted
	CryptoBoxUserConfiguration	CryptoBoxUserDailyUse	CryptoBoxDev
	CryptoBoxDevPreparation	CryptoBoxDevCustomBuild	CryptoBoxDevWorkFlow
	CryptoBoxDevValidation	CryptoBoxDevCustomConfigure	CryptoBoxDevBackground
	CryptoBoxDevKnownProblems"
#PAGES="CryptoBox"

# base URL
WIKI_HOST="https://systemausfall.org"
# the trailing slash is important
WIKI_URL=/trac/cryptobox/wiki/

CBOX_CGI="/doc?page="

LANGUAGES="de en"

DEST_DIR="$ROOT_DIR/doc/html"
OFFLINE_DIR="$ROOT_DIR/../live-cd/live-cd-tree.d/_offline/doc"
IMAGE_DIR="$ROOT_DIR/cbox-tree.d/var/www/cryptobox-misc"
TMP_DIR=/tmp/$(basename $0)-$$.d

HEADER_FILE=doc_header.inc
FOOTER_FILE=doc_footer.inc

WGET_OPTS="--quiet --no-check-certificate"

[ ! -e "$DEST_DIR" ] && echo "$DEST_DIR does not exist" && exit 1

for LANG in $LANGUAGES; do
	for PAGE in $PAGES; do
		PAGE_SRC="$WIKI_HOST$WIKI_URL$PAGE/$LANG"
		echo "Importing $PAGE/$LANG:"

		# replace sub-page-style '/' like moin does it (by '_2f')
		TMP_FILE=$TMP_DIR/${PAGE}.html
		mkdir -p "$TMP_DIR"

		echo "	downloading the page ..."
		wget $WGET_OPTS --output-document="$TMP_FILE" "$PAGE_SRC" || { echo "Downloading ($PAGE_SRC) failed!"; exit 1; }

		# check if this page exists
		if grep -q "^describe $PAGE/$LANG here$" "$TMP_FILE"
		  then	rm "$TMP_FILE"
				PAGE_SRC=$(dirname $PAGE_SRC)
				echo "	trying to download default language page instead"
				wget $WGET_OPTS --output-document="$TMP_FILE" "$PAGE_SRC" || { echo "Downloading ($PAGE_SRC) failed!" >&2; exit 1; }
				# check, if there is even no default page
				grep -q "^describe $PAGE/$LANG here$" "$TMP_FILE" && echo "This page ($PAGE_SRC) was not found!" >&2 && exit 1
		  fi

		echo "	removing header and footer ..."
		# break lines before start of content
		sed -i 's#<div id="content" class="wiki">#_END_OF_HEADER_\n#' "$TMP_FILE"
		# the 'edit' buttons mark the end of the page
		sed -i 's#<div class="buttons">#\n_START_OF_FOOTER_#' "$TMP_FILE"
		# cut off a possible comment - section
		sed -i "s#<form action=[^>]*\#commentpreview#\n_START_OF_FOOTER_#" "$TMP_FILE"
		# remove all lines before and after "body"
		sed -i '1,/_END_OF_HEADER_/d; /_START_OF_FOOTER_/,$d' "$TMP_FILE"

		# close open divs
		while [ "$(grep '<div' "$TMP_FILE" | wc -l)" -gt "$(grep '</div>' "$TMP_FILE" | wc -l)" ]
			do	echo "</div>" >>"$TMP_FILE"
		  done

		#echo "	removing link images (moin specific) ..."
		# remove inter-wiki images
		#sed -i 's#<[^<]*moin-inter.png[^>]*>##g' "$TMP_FILE"
		# remove moin-www images
		#sed -i 's#<[^<]*moin-www.png[^>]*> ##g' "$TMP_FILE"

		# not necessary, because everything is a part of the repository
		#echo "	downloading requisites ..."
		#wget --quiet --ignore-tags=a --no-clobber --page-requisites --convert-links --no-directories --base="$WIKI_HOST$WIKI_URL" --directory-prefix="$TMP_DIR" --html-extension --force-html --input-file="$TMP_FILE" || { echo "Downloading requisites for ($PAGE_SRC) failed!"; exit 1; }

		echo "	adjusting links for images ..."
		sed -i "s#='[^']*/cryptobox-misc/\([^']*\)'#='/cryptobox-misc/\1'#g" "$TMP_FILE"

		echo "	adjusting wiki links ..."
		# redirect wiki links to cryptobox cgi
		sed -i "s#=\"$WIKI_URL\([^\.]*\)\"#=\"$CBOX_CGI\1\"#g" "$TMP_FILE"
		# do it twice - somehow, the "g" flag does not work (it should replace multiple occurrences on a line)
		sed -i "s#=\"$WIKI_URL\([^\.]*\)\"#=\"$CBOX_CGI\1\"#g" "$TMP_FILE"
		# remove language specific part of moin link
		for TLANG in $LANGUAGES
			do	sed -i "s#=\"$CBOX_CGI\([^\"]*\)/$TLANG#=\"$CBOX_CGI\1#g" "$TMP_FILE"
		  done

		
		# build the static pages
		echo "	building static doc page"
		offline_file=$OFFLINE_DIR/$LANG/$(basename $TMP_FILE)
		mkdir -p "$OFFLINE_DIR/$LANG"
		cat "$OFFLINE_DIR/$HEADER_FILE" "$OFFLINE_DIR/$LANG/$HEADER_FILE" "$TMP_FILE" "$OFFLINE_DIR/$LANG/$FOOTER_FILE" "$OFFLINE_DIR/$FOOTER_FILE" >"$offline_file"
		sed -i "s%=\"$CBOX_CGI\([^\"#]*\)%=\"\1.html%g" "$offline_file"
		# do it twice - this should not be necessary
		sed -i "s%=\"$CBOX_CGI\([^#\"]*\)%=\"\1.html%g" "$offline_file"
		sed -i "s#='/cryptobox-misc#='../../../var/www/cryptobox-misc#g" "$offline_file"

		# split language specific part of moin link and replace it by current language
		for TLANG in $LANGUAGES
			do	sed -i "s#=\"\([^/]*\)/${TLANG}.html\"#=\"\1.html\"#g" "$offline_file"
		  done

		# some last changes to the dynamic pages (must be done _after_ the static pages)
		# add weblang for current language to query string
		sed -i "s;=\"$CBOX_CGI\([^#\"]*\)\([#\"]\);=\"$CBOX_CGI\1\&weblang=$LANG\2;g" "$TMP_FILE"
		# move cgi-doc
		mv "$TMP_FILE" "$DEST_DIR/$LANG"

		echo "	finished!"
	  done
  done

[ -n "$(find "$TMP_DIR" -type f)" ] &&  mv "$TMP_DIR"/* "$IMAGE_DIR"
rmdir "$TMP_DIR"
