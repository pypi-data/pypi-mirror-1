set -e

urlprefix='http://127.0.0.1/test/data/zip/test/try.zip'
#urlprefix='http://127.0.0.1/test/data/zip/test/try.tar'

#identifier='/tt\[\]'
#data="remote try a line"

identifier='/1/2/3/4/tt1\[\]'
data="remote try a few depth deeper"

curl -X PUT --data "$data" "$urlprefix/$identifier"
curl -X GET --data "$data" "$urlprefix/$identifier"

#identifier='/img/tk.gif\[\]'
#curl -X PUT --data-binary @/usr/lib64/python2.4/idlelib/Icons/tk.gif "$urlprefix/$identifier"
