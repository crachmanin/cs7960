for d in configs/config$1* ; do
	#echo $d
	( cd $d && cp ../../mnist_mlp.h5 . && snntoolbox -t $(basename $d)) 
done
