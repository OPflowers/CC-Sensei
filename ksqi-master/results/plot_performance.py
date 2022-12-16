import numpy as np
import matplotlib.pyplot as plt
import os

bba_traces = "../../pensieve/test/results/bba/"
pensieve_traces = "../../pensieve/test/results/pensieve/"
sensei_traces = "../../pensieve/test/results/sensei/"


def get_average_throughput(file):
    # print(file)
    throughput = 0
    line_count = 0
    with open(file, 'r') as f:
        for line in f:
            if len(line.split("\t")) > 1:
                throughput += float(line.split("\t")[1])
                line_count += 1
    return throughput/line_count


def get_throughputs_for_files_in_directory(directory):
    throughputs = []
    for file in os.listdir(directory):
        throughputs.append(get_average_throughput(directory + file))
    return throughputs


def get_throughput_for_file_group(directory_base, files):
    throughputs = []
    for file in files:
        throughputs.append(get_average_throughput(directory_base + file))
    return throughputs


def plot_throughput():
    bba_throughputs = get_throughputs_for_files_in_directory(bba_traces)
    print(bba_throughputs)

    pensieve_throughputs = get_throughputs_for_files_in_directory(pensieve_traces)
    print(pensieve_throughputs)

    sensei_throughputs = []
    for video in range(0, 8):
        traces_for_video = [s for s in os.listdir(sensei_traces) if "video" + str(video) in s]
        sensei_throughputs.append(np.mean(get_throughput_for_file_group(sensei_traces, traces_for_video)))

    print(sensei_throughputs)

    plt.plot(bba_throughputs)
    plt.plot(pensieve_throughputs)
    plt.plot(sensei_throughputs)
    plt.show()
    return


def main():
    plot_throughput()
    return


if __name__ == "__main__":
    main()
