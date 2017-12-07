#!/bin/bash

if [ ! -d "$DIRECTORY" ]; then
	./gen_env.sh
fi	 

source venv/bin/activate
for d in configs/config$1* ; do
	#echo $d
	( cd $d && cp ../../mnist_mlp.h5 . && snntoolbox -t $(basename $d)) 
done
