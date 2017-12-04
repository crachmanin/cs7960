for d in configs/* ; do
    ( cd $d && cp ../mnist_mlp.h5 . && snntoolbox -t $d ) 
done
