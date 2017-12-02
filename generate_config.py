import glob
import os

default_params = {
    "paths" : {
        "dataset_path" : "\%(path_wd)s/../../../datasets/mnist",
        "filename_ann" : "mnist_mlp"
    },
    "input" : {
        "poisson_input" : "False"
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
    (("simulation", "duration"), ["10", "20"])
]

def generate_permutations(result, output, index):
    if index > 5:
        result.append(dict(output))
        return

    for val in params[index][1]:
        section, param = params[index][0]

        if section not in output:
            output[section] = {}

        output[section][param] = val
        generate_permutations(result, output, index + 1)


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
    for neuron_fn in neuron_fns:
        neuron_dict = neuron_to_dict(neuron_fn)
        output = dict(default_params)
        output["cell"] = neuron_dict
        generate_permutations(result, output, 0)

    for i, config_dict in enumerate(result):
        fn = os.path.join("configs", "config{0:0=3d}".format(i))
        with open(fn, 'w') as fp:
            config_str = dict_to_str(config_dict)
            fp.write(config_str)

if __name__ == "__main__":
    main()

