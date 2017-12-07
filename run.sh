#!/bin/bash

if [ ! -d venv ]; then
	./gen_env.sh
fi	 

python generate_config_new.py

source venv/bin/activate

for d in configs/config$1* ; do
	#echo $d
	( cd $d && cp ../../mnist_mlp.h5 . && snntoolbox -t $(basename $d)) 
done
