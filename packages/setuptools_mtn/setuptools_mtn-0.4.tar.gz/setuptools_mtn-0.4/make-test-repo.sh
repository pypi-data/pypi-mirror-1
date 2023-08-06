#!/bin/bash

set -e

MTN=${MTN:-mtn}

die() {
	echo "fatal: $*" >&2
	exit 1
}

xmtn() {
	"$MTN" "$@"
}

xmtn_rm() {
	# At some point mtn rm stopped needing -e to make filesystem
	# changes.  I think this method should work with both old and new
	# Monotone.
	rm "$@"
	xmtn rm "$@"
}
xmtn_mv() {
	# See comment for xmtn_rm, same principle applies here.
	mv "$@"
	xmtn mv "$@"
}

make_and_add() {
	[ $# -eq 2 ] || usage "$FUNCNAME <file name> <content>"
	local file=$1 content=$2
	echo "$content" >"$file"
	xmtn add "$file"
}

make_new_content() {
	[ $# -eq 1 ] || usage "$FUNCNAME <file name prefix>"
	local prefix=$1
	make_and_add "$prefix"_changing_content "changing content prefix=$prefix"
	make_and_add "$prefix"_renaming_content "renamed content prefix=$prefix"
	make_and_add "$prefix"_removed_content "removed content prefix=$prefix"
	make_and_add "$prefix"_disappearing_content "disappearing prefix=$prefix"
}

make_changes_to_content() {
	[ $# -eq 1 ] || usage "$FUNCNAME <file name prefix>"
	local prefix=$1
	make_and_add "$prefix"_new_content "new content prefix=$prefix"
	echo "changed content prefix=$prefix" >"$prefix"_changing_content
	local old_name=${prefix}_renaming_content
	local new_name=${prefix}_renamed_content
	xmtn_mv "$old_name" "$new_name"
	[ ! -e "$old_name" -a -e "$new_name" ] || die "renaming failed?"
	xmtn_rm "$prefix"_removed_content
	rm "$prefix"_disappearing_content
}

if [ $# -eq 0 ]; then
	root=$(mktemp -t -d)
elif [ $# -eq 1 ]; then
	root=$1
else
	die "usage: $(basename "$0") [ <root dir> ]"
fi
echo "root=$root"

mkdir -p "$root"
cd "$root"
db=$PWD/db
[ ! -e "$db" -a ! -e "repo" ] || die "db and/or repo already exist"
xmtn db init --db="$db"
mkdir repo
cd repo
xmtn setup --db="$db" --branch="test.branch"

make_new_content base
mkdir subdir1
make_new_content subdir1/sub1
mkdir prefix
make_and_add prefix/content "prefix's content"
mkdir prefixtrick
make_and_add prefixtrick/content "prefixtrick's content"
xmtn commit -m "stage 1"

make_changes_to_content base
make_changes_to_content subdir1/sub1
mkdir subdir2
make_new_content subdir2/sub2

touch unknown_file
mkdir unknown_subdir
touch unknown_subdir/unknown_subdir_file

echo "$root"
echo "OK"
