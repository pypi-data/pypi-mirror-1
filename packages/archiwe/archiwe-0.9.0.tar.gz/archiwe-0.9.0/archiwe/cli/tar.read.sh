source ./common.read.sh

#path='/home/webifier/test/data/tar/blas-sciflo-0.1.tar.gz'
#path='/home/webifier/test/data/tar/blas-sciflo-0.1.tar'
#path='/home/webifier/test/data/tar/Python-2.5.4.tar.bz2'
#path='/home/webifier/test/data/tar/h5py-1.2.0.tar.gz'
path='/home/webifier/test/data/tar/hdf5-1.6.5.tar.gz'

type=tar

cacheDir="--cacheDir $cacheTopDir/tar"
#cacheDir=""
#reCache="--reCache"
reCache=""
traverse="--traverse"
#traverse=""

#output="--output html"
output=""

python $cmd --type $type $output $traverse $cacheDir $reCache "$path" '/'
#python $cmd --type $type $output $traverse $cacheDir $reCache "$path" '/hdf5-1.6.5/'
#python $cmd --type $type $output $traverse $cacheDir $reCache "$path" '/hdf5-1.6.5/doc/'
#python $cmd --type $type $output $traverse $cacheDir $reCache "$path" '/hdf5-1.6.5/bin/config.guess[]'
