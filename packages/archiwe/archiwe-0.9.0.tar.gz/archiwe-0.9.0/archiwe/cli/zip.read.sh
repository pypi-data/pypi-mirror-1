source ./common.read.sh

# do not bother with this now!
#path='/usr/local/RAID Web Console 2/jre/lib/deploy/ffjcext.zip'
#python $cmd --type zip "$path" '/\{CAFEEFAC-0016-0000-0000-ABCDEFFEDCBA\}/'

#path='/home/webifier/test/data/zip/simple.zip'
#path='/usr/lib64/openoffice.org/share/config/wizard/web/buttons/simple.zip'
path='/home/webifier/test/data/zip/Win32.zip'
type=zip

cacheDir="--cacheDir $cacheTopDir/zip"
#cacheDir=""
#reCache="--reCache"
reCache=""
#traverse="--traverse"
traverse=""

#output="--output html"
output=""

python $cmd --type $type $output $traverse $cacheDir $reCache "$path" '/'
#python $cmd --type $type $output $traverse $cacheDir $reCache "$path" '/ncgen.dsp/'
#python $cmd --type $type $traverse "$path" '/hdf/'
#python $cmd --type $type --output json --callback try "$path" '/ncgen.dsp/'
#python $cmd --type $type $output "$path" '/ncgen.dsp[]'
#python $cmd --type $type "$path" '/ncgen.dsp[]'
#python $cmd --type $type $output $traverse $cacheDir $reCache "$path" '/ncgen.dsp[]'
