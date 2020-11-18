#!/usr/bin/env bash

python extract-relations.py > relations.log

pushd tweets/with_rel

for i in `fd -t e -e txt`;
do
	echo "Removing empty $i" && rm "$i"
done

popd

mv tweets/with_rel ./related
mkdir tweets/with_rel
