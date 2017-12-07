import pickle
import os.path
import numpy as np

def generateCSV(data, column_order, file_name):
	
	# Removes file if it already exists
	try:
		os.remove(file_name)
	except OSError:
		pass
	
	csv_file = open(file_name, 'a')
	
	initial_line = ""
	for current_column in column_order:
		initial_line += (current_column + ",")
	csv_file.write(initial_line + "\n")
	
	for current_key in data.keys():
		current_line = ""
		for current_column in column_order:
			if current_column in data[current_key]:
				current_line += (str(data[current_key][current_column]) + ",")
			else:
				current_line += ","
		current_line += "\n"
		csv_file.write(current_line)
	csv_file.close()

def averageAccuracy(path):
	top_1_accuracy = float(-1)
	top_5_accuracy = float(-1)
	
	accuracy_file = open(path)
	for current_line in accuracy_file:
		current_accuracies = current_line.split()
		top_1_accuracy = float(current_accuracies[1].strip('%'))/100
		top_5_accuracy = float(current_accuracies[2].strip('%'))/100
		#if top_1_accuracy < 0 or top_5_accuracy <0:
		#	top_1_accuracy = float(current_accuracies[1].strip('%'))/100
		#	top_5_accuracy = float(current_accuracies[2].strip('%'))/100
		#else:
		#	top_1_accuracy = (top_1_accuracy + (float(current_accuracies[1].strip('%'))/100))/2
		#	top_5_accuracy = (top_5_accuracy + (float(current_accuracies[1].strip('%'))/100))/2
	
	accuracy_file.close()
	return (top_1_accuracy, top_5_accuracy)

def importConfigParameters(path, data, current_directory):
	config_file = open(path)
	for current_line in config_file:
		current_value = current_line.split("=")
		if not len(current_value) <= 1:
			data[current_directory][current_value[0].strip()] = current_value[1].strip()


def averageSpikeCount(path):
	total_spike_count = -1

	for file in os.listdir(path):
		try:
    			if file.endswith(".npz"):
        			current_batch = np.load(path + "/" + file)
				spiketrains_n_b_l_t = current_batch.f.spiketrains_n_b_l_t
				#print ("reading batch file: " + file)
			
				# batch time dimensions
				b_t_shape = (spiketrains_n_b_l_t[0][0].shape[0],
                	 	spiketrains_n_b_l_t[0][0].shape[-1])
    				spikecounts_b_t = np.zeros(b_t_shape)
	    			for n in range(len(spiketrains_n_b_l_t)):  # Loop over layers
        				spiketrains_b_l_t = np.not_equal(spiketrains_n_b_l_t[n][0], 0)
        				reduction_axes = tuple(np.arange(1, spiketrains_b_l_t.ndim-1))
        				spikecounts_b_t += np.sum(spiketrains_b_l_t, reduction_axes)
    				cum_spikecounts_b_t = np.cumsum(spikecounts_b_t, 1)

				(batch_size, duration_length) = cum_spikecounts_b_t.shape
				batch_average = -1
				for current_test in cum_spikecounts_b_t:
					current_spike_count = current_test[duration_length-1]
					if batch_average < 0:
						batch_average = current_spike_count
					else:
						batch_average = (batch_average + current_spike_count)/2
			
				if total_spike_count < 0:
					total_spike_count = batch_average
				else:
					total_spike_count = (total_spike_count + batch_average)/2
		except:
			print ("an error occured while calculating file: " + file)
			pass

	return total_spike_count


data = {}
parameters = ["name", "path_wd", "dataset_path", "log_dir_of_current_run", "runlabel", "filename_ann", "filename_parsed_model", "filename_snn", "filename_clamp_indices", "class_idx_path", "model_lib", "dataset_format", "datagen_kwargs", "dataflow_kwargs", "poisson_input", "input_rate", "num_poisson_events_per_sample", "num_dvs_events_per_sample", "eventframe_width", "label_dict", "chip_size", "frame_gen_method", "is_x_first", "is_x_flipped", "is_y_flipped", "evaluateANN", "normalize", "convert", "simulate", "percentile", "normalization_schedule", "online_normalization", "diff_to_max_rate", "diff_to_min_rate", "timestep_fraction", "softmax_to_relu", "maxpool_type", "max2avg_pool", "spike_code", "num_bits", "simulator", "duration", "dt", "num_to_test", "sample_idxs_to_test", "batch_size", "reset_between_nth_sample", "top_k", "keras_backend", "v_thresh", "v_reset", "v_rest", "e_rev_E", "e_rev_I", "i_offset", "cm", "tau_m", "tau_refrac", "tau_syn", "tau_synn_I", "delay", "binarize_weights", "scaling_factor", "payloads", "reset", "leak", "param_values", "param_name", "param_logscale", "log_vars", "plot_vars", "verbose", "overwrite", "plotproperties", "top_1_accuracy", "top_5_accuracy", "average_spike_count"]

if os.path.isfile("data.pickle"):
	pickle_in = open("data.pickle","rb")
	data = pickle.load(pickle_in)
	pickle_in.close()
	print 'pickled data found and loaded.'

for x in os.walk("configs/"):
	current_directory = x[0]
	
	#determines if the current directory has a log folder
	if os.path.isdir(current_directory + "/log"):
		if not current_directory in data:
			data[current_directory] = {}

		# adds directory to dictionary
		print ("sub-directory: " + current_directory + "'has log")
		data[current_directory]["name"] = current_directory

		# adds config data to dictionary
		config_path = current_directory + "/" + current_directory.split("/")[1]
		importConfigParameters(config_path, data, current_directory)
		
		if not "top_1_accuracy" in data[current_directory]:
			# calculates the accuracies
			accuracy_path = (current_directory + "/log/gui/test/accuracy.txt")
			(top_1, top_5) = averageAccuracy(accuracy_path)
			data[current_directory]["top_1_accuracy"] = top_1
			data[current_directory]["top_5_accuracy"] = top_5

		if not "average_spike_count" in data[current_directory]:
			# calculates the average spike count for the current configuration
			spike_count_path = (current_directory + "/log/gui/test/log_vars")
			average_spike_count = averageSpikeCount(spike_count_path)
			data[current_directory]["average_spike_count"] = average_spike_count

pickle_out = open("data.pickle", "wb")
pickle.dump(data, pickle_out)
pickle_out.close()

generateCSV(data, parameters, "results.csv")

