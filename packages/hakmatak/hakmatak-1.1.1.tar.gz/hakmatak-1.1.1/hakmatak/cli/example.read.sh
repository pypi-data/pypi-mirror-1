source ./common.read.sh

path='a_fake_path'

#type=example
type=example.basic

cacheDir="--cacheDir $cacheTopDir/$type"
#cacheDir=""
reCache="--reCache"
#reCache=""
#traverse="--traverse"
traverse=""

#output="--output html"
output=""

#python $cmd --type $type $traverse "$path" '/'
python $cmd --type $type $output $traverse $cacheDir $reCache "$path" '/'
#python $cmd --type $type "$path" '/leaf0/'
#python $cmd --type $type "$path" '/leaf1/'
#python $cmd --type $type "$path" '/node0/leaf/'
#python $cmd --type $type "$path" '/node0/'
#python $cmd --type $type "$path" '/node0[]'
#python $cmd --type $type $traverse "$path" '/node/'
#python $cmd --type $type "$path" '/node/leaf[]'
#python $cmd --type $type "$path" '/node/node A/'
#python $cmd --type $type "$path" '/node/node A/leaf/'
#python $cmd --type $type "$path" '/node/node A/leaf'
#python $cmd --type $type "$path" '/node/node A/leaf[]'
#python $cmd --type $type "$path" '/node/node A/leaf[2]'
