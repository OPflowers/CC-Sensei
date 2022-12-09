import os
import numpy as np
trace_folder = "./converted_traces/"
out_path = "./cooked_traces/"
VIDEO_LENGTH = 20
if not os.path.exists(out_path):
    os.mkdir(out_path)

for file in os.listdir(trace_folder):
    name, ext = file.split(".")
    new_name = "cooked_" + name
    with open(out_path + new_name + "." + ext, 'w') as write_file, open(trace_folder + file, 'r') as read_file:
        timestamps = []
        throughputs = []
        for line in read_file:
            timestamp, throughput = line.split()
            timestamps.append(float(timestamp))  # seconds
            throughputs.append(throughput)  # convert to Mbits within 0.2 - 6 Mbps range

        np_timestamps = np.asarray(timestamps)
        np_timestamps = (np_timestamps - np.min(np_timestamps)) / (
                    np.max(np_timestamps) - np.min(np_timestamps)) * VIDEO_LENGTH

        for i in range(0, len(np_timestamps)):
            write_file.write(str(np_timestamps[i]) + " " + throughputs[i] + "\n")

