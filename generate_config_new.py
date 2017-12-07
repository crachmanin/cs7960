import glob
import os
import copy

'''
[cell]
v_thresh = 10
tau_refrac = 1
v_reset = 0
v_rest = -65.0
e_rev_E = 10
e_rev_I = -10
i_offset = 0
cm = 1.0
tau_m = 20.0
tau_syn_E = 5.0
tau_syn_I = 5.0
delay = 1
binarize_weights = False
quantize_weights = False
scaling_factor = 10000000
payloads = False
reset = Reset by subtraction
leak = True
'''
default_params = {
    "cells" : {
	"v_thresh" : "10",
	"tau_refrac" : "1",
	"v_reset" : "0",
	"v_rest" : "-65.0",
	"e_rev_E" : "10",
	"e_rev_I" : "-10",
	"i_offset" : "0",
	"cm" : "1.0",
	"tau_m" : "20.0",
	"tau_syn_E" : "5.0",
	"tau_syn_I" : "5.0",
	"delay" : "1",
	"binarize_weights" : "False",
	"quantize_weights" : "False",
	"scaling_factor" : "10000000",
	"payloads" : "False",
	"reset" : "Reset by subtraction",
	"leak" : "True"
    },
    "paths" : {
        "dataset_path" : "%(path_wd)s/../../datasets/mnist",
        "filename_ann" : "mnist_mlp"
    },
    "input" : {
        "poisson_input" : "False"
    },
    "tools" : {
        "normalize" : "False"
    },
    "output" : {
        "log_vars" : "{'all'}",
        "plot_vars" : "{'all'}"
    },
    "simulation" : {
        "simulator" : "INI",
        "num_to_test" : "10000",
        "batch_size" : "100"
    }
}

params = [
    (("conversion", "softmax_to_relu"), ["True", "False"]),
    (("conversion", "maxpool_type"), ['fir_max', 'exp_max', 'avg_max']),
    (("conversion", "max2avg_pool"), ["True", "False"]),
    (("conversion", "spike_code"), ["temporal_mean_rate", "temporal_pattern"]),
    (("conversion", "num_bits"), ["16", "32", "64"]),
    (("simulation", "duration"), ["20", "30"])
]

def generate_permutations(result, output, index):
    if index > 5:
        result.append(dict(output))
        return

    for val in params[index][1]:
        section, param = params[index][0]

	out_copy = copy.deepcopy(output)

        if section not in output:
            out_copy[section] = {}

        out_copy[section][param] = val
        generate_permutations(result, out_copy, index + 1)


def neuron_to_dict(neuron_file):
    result = {}
    with open(neuron_file) as fp:
        for line in fp:
            [param, val] = line.split()
            result[param] = val

    return result


def dict_to_str(config_dict):
    result = []
    for section in config_dict:
        result.append("[" + section + "]")

        for param in config_dict[section]:
            result.append(param + " = " + config_dict[section][param])

        result.append('\n')

    return '\n'.join(result)


def main():
    neuron_fns = glob.glob("neuron_types/*")
    result = []
    #for neuron_fn in neuron_fns:
    #    neuron_dict = neuron_to_dict(neuron_fn)
    output = dict(default_params)
    #    output["cell"] = neuron_dict
    generate_permutations(result, output, 0)

    for i, config_dict in enumerate(result):
	print (config_dict)
	name = "config{0:0=3d}".format(i)
        fn = os.path.join("configs", name, name)
	if not os.path.exists(os.path.dirname(fn)):
    	    try:
                os.makedirs(os.path.dirname(fn))
    	    except OSError as exc:
        	if exc.errno != errno.EEXIST:
            	    raise
        with open(fn, 'w') as fp:
            config_str = dict_to_str(config_dict)
            fp.write(config_str)

if __name__ == "__main__":
    main()

