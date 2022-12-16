import argparse
import os
import subprocess
import videoeffects


def main():
    # generate new "sensei-d" videos; videos with delays
    base_video_output_folder = "./Augmented Videos/Generated Videos/"
    base_sensei_traces = "./pensieve/test/results/sensei/"
    original_video_folder = "./Youtube Videos/Youtube UGC Videos Raw/"
    trace_no = 0
    for file in os.listdir(base_sensei_traces):
        bitrates = []  # create videos with delays
        with open(base_sensei_traces + file, 'r') as f:
            for line in f:
                if len(line) > 1:
                    bitrates.append(float(line.split("\t")[1]))

        for video_file in os.listdir(original_video_folder):
            if video_file.endswith('.mp4'):
                output_name = base_video_output_folder + "sensei_trace_" + str(trace_no) + "-" + video_file
                videoeffects.set_video_bitrates(original_video_folder + video_file, 1, bitrates, output_name)
        trace_no += 1
    return


if __name__ == "__main__":
    main()
