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

path='/home/webifier/test/data/grib/note.txt'
python $cmd --type $type $output $traverse $cacheDir $reCache "$path" '/'
#python $cmd --type $type $output $traverse $cacheDir $reCache "$path" '/0/'

exit

path='/usr/local/share/pcs.csv'
#python $cmd --type $type $output $traverse $cacheDir $reCache "$path" '/'
#python $cmd --type $type $output $traverse $cacheDir $reCache "$path" '/262144/'
python $cmd --type $type $output $traverse $cacheDir $reCache "$path" '/0/114688/'
#python $cmd --type $type $output $traverse $cacheDir $reCache "$path" '/0/114688/116288/'
#python $cmd --type $type $output $traverse $cacheDir $reCache "$path" '/0/114688/116288[]'
