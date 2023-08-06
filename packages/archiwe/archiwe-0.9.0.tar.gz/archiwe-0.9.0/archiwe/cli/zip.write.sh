#!/bin/bash

source ./common.write.sh

path="./test.zip"

type=zip

data="this is a try 1"
python $cmd --type $type --data "$data" "$path" '/ttt[]'
data="this is a try 2"
python $cmd --type $type --data "$data" "$path" '/ttt1[]'
data="this is a try 3"
python $cmd --type $type --data "$data" "$path" '/ttt2[]'
python $cmd --type $type --data "$data" "$path" '/t/rt3[]'
python $cmd --type $type --data "$data" "$path" '/t[]'
data="a rather long string"
python $cmd --type $type --data "$data" "$path" '/t/ter/erg/er/er/erherth/wef[]'
