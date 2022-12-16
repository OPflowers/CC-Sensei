import numpy as np
import matplotlib.pyplot as plt
import os
from pensieve.test.get_qoe_by_chunk_for_video import get_weights_for_chunks

bba_traces = "../../pensieve/test/results/bba/"
pensieve_traces = "../../pensieve/test/results/pensieve/"
sensei_traces = "../../pensieve/test/results/sensei/"


sensei_qoe_models_path = "./custom_data/"


def read_performance_log(file):
    results = []
    first_line = True
    with open(file, 'r') as f:
        for line in f:
            if first_line:
                first_line = False
                continue
            if len(line) > 1:
                model, plcc, srcc, krcc = line[:-1].split(",")
                results.append([model, float(plcc), float(srcc), float(krcc)])

    return results


def read_score_log(file):
    chunks = 8

    chunk_count = 0
    first_line = True
    video_qoe_container = [] # contains [[video1_1, video1_2, ..][video2_1, video2_2, ...] ...]
    with open(file, 'r') as f:
        video_qoe_list = []
        for line in f:
            if first_line:
                first_line = False
                continue
            if len(line) > 1:
                video_log = line.split(",")
                video_qoe_list.append(float(video_log[1]))
                chunk_count += 1

            if chunk_count == chunks:
                chunk_count = 0
                video_qoe_container.append(video_qoe_list)
                video_qoe_list = []
    return video_qoe_container


def get_throughput(file, rebuffer):
    throughput = []
    do_rebuffer = []
    with open(file, 'r') as f:
        for line in f:
            if len(line.split("\t")) > 1:
                throughput.append(float(line.split("\t")[1]))
                if rebuffer:
                    do_rebuffer.append(float(line.split("\t")[-1]))
                    # print(float(line.split("\t")[-1]))
                else:
                    do_rebuffer.append(0)
    # print(do_rebuffer)
    return throughput, do_rebuffer


def get_average_throughput(file, rebuffer):
    # print(file)
    throughput = 0
    line_count = 0
    with open(file, 'r') as f:
        for line in f:
            if len(line.split("\t")) > 1:
                throughput += float(line.split("\t")[1])
                if rebuffer:
                    do_rebuffer = float(line.split("\t")[-1])
                    line_count += do_rebuffer
                line_count += 1
    return throughput / line_count


def get_throughputs_for_files_in_directory(directory, rebuffer):
    throughputs = []
    individual_throughputs = []
    individual_rebuffering = []
    for file in os.listdir(directory):
        throughputs.append(get_average_throughput(directory + file, rebuffer))
        ind_throughput, ind_rebuff = get_throughput(directory + file, rebuffer)
        individual_throughputs.append(ind_throughput)
        individual_rebuffering.append(individual_rebuffering)
    return throughputs, individual_throughputs, individual_rebuffering


def get_throughput_for_file_group(directory_base, files, rebuffer):
    throughputs = []
    individual_throughputs = []
    individual_rebuffering = []
    for file in files:
        throughputs.append(get_average_throughput(directory_base + file, rebuffer))
        ind_throughput, ind_rebuff = get_throughput(directory_base + file, rebuffer)
        individual_throughputs.append(ind_throughput)
        individual_rebuffering.append(ind_rebuff)
        # print(individual_rebuffering)
    # print(individual_rebuffering[0])
    return throughputs, individual_throughputs, individual_rebuffering


def plot_throughput(plot_individual):
    bba_throughputs, bba_ind_throughputs, bba_ind_rebuffers = get_throughputs_for_files_in_directory(bba_traces, False)
    print(bba_throughputs)

    pensieve_throughputs, pensieve_ind_throughputs, pensieve_ind_rebuffer = get_throughputs_for_files_in_directory(pensieve_traces, False)
    print(pensieve_throughputs)

    sensei_throughputs = []
    sensei_ind_throughputs = []
    sensei_ind_rebuffers = []
    for video in range(0, 8):
        traces_for_video = [s for s in os.listdir(sensei_traces) if "video" + str(video) in s]
        video_avg_throughput, video_ind_throughput, video_ind_rebuffer = get_throughput_for_file_group(sensei_traces, traces_for_video, True)
        sensei_throughputs.append(video_avg_throughput)
        sensei_ind_throughputs.append(video_ind_throughput)

        sensei_ind_rebuffers.append(video_ind_rebuffer)

    if plot_individual:
        for trace in range(0, len(bba_ind_throughputs)):
            for video in range(0, 8):
                print(bba_ind_throughputs[trace])
                print(pensieve_ind_throughputs[trace])
                print(sensei_ind_throughputs[video][trace])
                # print(sensei_ind_rebuffers[video][trace][0])



                x = np.arange(len(bba_ind_throughputs[trace]))

                fig, ax1 = plt.subplots()
                ax1.plot(x, bba_ind_throughputs[trace], label="BBA")
                ax1.plot(x, pensieve_ind_throughputs[trace], label="BBA")
                ax1.plot(x, sensei_ind_throughputs[video][trace], label="SENSEI-Pensieve")
                ax1.legend()
                ax1.set_ylabel("Bitrate (Kbps)")
                ax2 = ax1.twinx()
                ax2.vlines(np.multiply(sensei_ind_rebuffers[video][trace], x), label="rebuffer", ymin=0, ymax=1, color='red')
                ax2.set_ylabel("Rebuffer state (1 = rebuffer, 0 = don't rebuffer)")
                ax2.legend()
                plt.xlabel("Chunk Number")
                plt.title("ABR trace output and SENSEI-Pensieve rebuffer places: trace " + str(trace) + ", video " + str(video))
                plt.show()

    sensei_throughputs = np.mean(np.array(sensei_throughputs), axis=0)
    print(sensei_throughputs)
    print(sensei_throughputs.shape)

    x = np.arange(len(bba_throughputs))
    plt.bar(x - 0.1, bba_throughputs, 0.1, label="BBA")
    plt.bar(x, pensieve_throughputs, 0.1, label="Pensieve")
    plt.bar(x + 0.1, sensei_throughputs, 0.1, label="Sensei-Pensieve")
    plt.xlabel("Trace")
    plt.ylabel("Bitrate (Mbps)")
    plt.legend()
    plt.title("Average Bitrate of Simulated Trace Selected by ABR")
    plt.show()
    return


def plot_individual_video_comparisons():
    categories = ["KSQI, SENSEI, Bentaleb2016, P1203"]
    ksqi_plcc = []
    sensei_plcc = []
    bentaleb_plcc = []
    p1203_plcc = []

    ksqi_srcc = []
    sensei_srcc = []
    bentaleb_srcc = []
    p1203_srcc = []

    videos = 8
    for i in range(0, videos):
        performance_log_name = "sensei_video" + str(i) + "_performance.csv"
        video_performance = read_performance_log(sensei_qoe_models_path + performance_log_name)
        for test in video_performance:
            if test[0] == 'KSQI':
                ksqi_plcc.append(test[1])
                ksqi_srcc.append(test[2])
            elif test[0] == 'SENSEI_KSQI':
                sensei_plcc.append(test[1])
                sensei_srcc.append(test[2])
            elif test[0] == 'Bentaleb2016QoE':
                bentaleb_plcc.append(test[1])
                bentaleb_srcc.append(test[2])
            else:
                p1203_plcc.append(test[1])
                p1203_srcc.append(test[2])

    x = np.arange(len(ksqi_plcc))
    plt.bar(x - 0.2, ksqi_plcc, 0.1, label="KSQI")
    plt.bar(x - 0.1, sensei_plcc, 0.1, label="SENSEI-KSQI")
    plt.bar(x, bentaleb_plcc, 0.1, label="Bentaleb2016QoE")
    plt.bar(x + 0.1, p1203_plcc, 0.1, label="P1203")
    plt.xlabel("Video Number")
    plt.ylabel("PLCC")
    plt.title("PLCC of QoE Models by Video")
    plt.legend()
    plt.show()

    x = np.arange(len(ksqi_srcc))
    plt.bar(x - 0.2, ksqi_srcc, 0.1, label="KSQI")
    plt.bar(x - 0.1, sensei_srcc, 0.1, label="SENSEI-KSQI")
    plt.bar(x, bentaleb_srcc, 0.1, label="Bentaleb2016QoE")
    plt.bar(x + 0.1, p1203_srcc, 0.1, label="P1203")
    plt.xlabel("Video Number")
    plt.ylabel("SRCC")
    plt.title("SRCC of QoE Models by Video")
    plt.legend()
    plt.show()
    return


def plot_video_qoe_comparisons():
    videos = 8

    labels = ["large chunk 1", "large chunk 2", "large chunk 3", "large chunk 4", "significant chunk 1", "significant chunk 2", "significant chunk 3", "significant chunk 4"]
    bba_qoe = read_score_log(sensei_qoe_models_path + "bb_scores.csv")
    pensieve_qoe = read_score_log(sensei_qoe_models_path + "pensieve_scores.csv")

    sensei_qoe_total = []
    for video in range(videos):
        sensei_qoe = read_score_log(sensei_qoe_models_path + "sensei_video" + str(video) + "_scores.csv")
        # print(np.asarray(sensei_qoe))
        sensei_qoe_total.append(np.mean(np.asarray(sensei_qoe), axis=0))
        # print(sensei_qoe_traces_averaged)
        # break
        weights = get_weights_for_chunks(video)
        print(weights)
        multiplied_weights = np.multiply(np.asarray(bba_qoe[video]),  np.asarray(weights))
        print(multiplied_weights)
        print(np.mean(multiplied_weights))
        # print(np.sum())
        # print(np.sum(np.asarray(pensieve_qoe[video]) * np.asarray(weights)))
        # print(np.sum(np.asarray(sensei_qoe_total[video]) * np.asarray(weights)))

        # print(bba_qoe[video])
        # print(pensieve_qoe[video])
        # print(sensei_qoe_total[video])
        x = np.arange(len(bba_qoe[0]))
        plt.bar(x - 0.1, bba_qoe[video], 0.1, label="BBA")
        plt.bar(x, pensieve_qoe[video], 0.1, label="Pensieve")
        plt.bar(x + 0.1, sensei_qoe_total[video], 0.1, label="Sensei")
        plt.xticks(x, labels)
        plt.title("KSQI QoE Model output of video " + str(video) + " with different bitrate by ABR algorithms")
        plt.ylabel("Modeled QoE")
        plt.xlabel("Video with incident inserted in [x] chunk")
        plt.legend()
        plt.show()


def main():
    plot_throughput(True)
    plot_individual_video_comparisons()
    plot_video_qoe_comparisons()
    return


if __name__ == "__main__":
    main()
