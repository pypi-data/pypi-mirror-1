source ./common.read.sh

type=bytearray

cacheDir="--cacheDir $cacheTopDir/$type"
#cacheDir=""
reCache="--reCache"
#reCache=""
#traverse="--traverse"
traverse=""

#output="--output html"
output=""

path='../../data/txt/test4.txt'
#python $cmd --type $type $output $traverse $cacheDir $reCache "$path" '/'
#python $cmd --type $type $output $traverse $cacheDir $reCache "$path" '/8192/8896/'
python $cmd --type $type $output $traverse $cacheDir $reCache "$path" '/8192/8896[]'
