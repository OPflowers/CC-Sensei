import pandas as pd
import numpy as np
import get_qoe_by_chunk_for_video
import subprocess
import os
import json
import cv2
import math
import argparse
import shutil

video_path_original = "../../Youtube Videos/Youtube UGC Videos Raw/"
video_path_augmented_phase_1 = "../../Augmented Videos/Phase 1/"
video_path_augmented_phase_2 = "../../Augmented Videos/Phase 2/with frame drops/"

video_names = ["08e1", "4b69", "2c06", "6658", "6403", "06a6", "2abf", "1a6d"]
phase_2_incidents = ["Frame Drop", "Frame Drop", "Freeze", "Freeze", "Frame Drop", "Freeze", "Freeze", "Frame Drop", ]
video_categories = ["Sports", "Sports", "Sports", "Gaming", "Gaming", "Animation", "Animation", "Animation", ]
CHANGED_FRAMERATE = 10
CHUNKS = 20
CHUNK_LEN = 4


# requires ffmpeg and libvmaf...
def get_video_quality_metrics(distorted, reference, video_no):
    assert os.path.exists(distorted) == True
    assert os.path.exists(reference) == True
    # command = ['echo', reference]
    path, end = distorted.split("-")
    if "phase_2" in end:
        name, ext = end.split(".")
    else:
        name, ext = end.split(".")
    version = name[-1]

    data_save_path = "./custom_data/vmaf_logs/" + name + "_vmaf.json"
    if os.path.exists(data_save_path):
        # print("calculating average metrics from json")
        cap = cv2.VideoCapture(distorted)
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(3))  # cv::CAP_PROP_FRAME_WIDTH =3,
        height = int(cap.get(4))  # cv::CAP_PROP_FRAME_HEIGHT =4,
        fps = int(cap.get(5))  # cv::CAP_PROP_FPS =5,
        # print(width)
        # print(height)
        with open(data_save_path) as json_file:
            vmaf = []
            psnr = []
            ssim = []
            data = json.load(json_file)
            # for k, v in data.items():
            #     print(k)
            # vmaf
            # psnr
            # ssim
            # global
            # input_file_dist
            # input_file_ref
            default_chunk_len = fps
            i = 0
            while i < len(data['vmaf']):
                # print(i)
                # average metrics by chunk
                next_chunk_len = min(default_chunk_len, len(data['vmaf']) - i)
                if next_chunk_len > 5:
                    vmaf_sum = 0
                    psnr_sum = 0
                    ssim_sum = 0
                    for j in range(0, next_chunk_len):
                        vmaf_sum += data['vmaf'][i + j]['vmaf']
                        psnr_sum += data['psnr'][i + j]['psnr_avg']
                        ssim_sum += data['ssim'][i + j]['ssim_avg']

                    vmaf.append(vmaf_sum / next_chunk_len)
                    psnr.append(psnr_sum / next_chunk_len)
                    ssim.append(ssim_sum / next_chunk_len)
                i += next_chunk_len

            return vmaf, psnr, ssim, fps, width, height
    else:
        command = ['ffmpeg-quality-metrics', distorted, reference, '-m', 'vmaf', 'psnr', 'ssim']
        print("running ffmpeg-quality-metrics")
        result = subprocess.run(command, stdout=subprocess.PIPE)
        with open(data_save_path, 'w') as f:
            f.write(result.stdout.decode('utf-8'))
        return get_video_quality_metrics(distorted, reference, video_no)
        # print(result)


def create_streaming_logs(bitrate_sim_file, video_no, out_path, abr):
    bitrates = []
    rebuffer_times = []
    with open(bitrate_sim_file, 'r') as f:
        for line in f:
            if len(line.split()) > 1:
                _, bitrate, _, rebuffer_time, _, _, _, do_rebuffer = line.split()
                bitrates.append(float(bitrate))
                if abr == "sensei":
                    rebuffer_times.append(float(rebuffer_time) * float(do_rebuffer))
                else:
                    rebuffer_times.append(float(rebuffer_time))

    bitrates = np.asarray(bitrates)
    rebuffer_times = np.asarray(rebuffer_times)

    # print(bitrates)
    video_name = video_names[video_no]
    print(video_name)
    original_video_name = ""
    for video in os.listdir(video_path_original):
        if video_name in video:
            original_video_name = video_path_original + video
            break

    augmented_videos = []
    for video in os.listdir(video_path_augmented_phase_1):
        if video_name in video:
            full_name, ext = video.split(".")
            description, simplified_name = full_name.split("-")
            video_id, version = simplified_name.split("_")
            if int(version) != get_qoe_by_chunk_for_video.get_phase_2_chunk(video_no):
                augmented_videos.append(video_path_augmented_phase_1 + video)
            else:

                for video_phase_2 in os.listdir(video_path_augmented_phase_2):
                    if video_name in video_phase_2:
                        augmented_videos.append(video_path_augmented_phase_2 + video_phase_2)

    # write to csv, create testing set
    # use same bitrate trace to compare QoE results
    for i in range(0, len(augmented_videos)):
        vmaf, psnr, ssim, fps, video_width, video_height = get_video_quality_metrics(augmented_videos[i],
                                                                                     original_video_name, video_no)
        # print(len(vmaf))
        # print(len(psnr))
        # print(len(ssim))

        version = int(augmented_videos[i].split(".")[-2][-1])
        # print("version: ", version)
        representation_index = np.ones(len(bitrates)) * video_no
        chunk_durations = np.ones(len(bitrates))
        rebuffering_duration = np.zeros(len(bitrates))
        framerate = np.ones(len(bitrates)) * fps
        height = np.ones(len(bitrates)) * video_height
        width = np.ones(len(bitrates)) * video_width
        # mos
        mos = np.ones(len(bitrates)) * get_qoe_by_chunk_for_video.get_video_qoe_by_chunks(
            video_no) * 20  # scale to x/100

        phase_2_chunk = get_qoe_by_chunk_for_video.get_phase_2_chunk(video_no)
        if "phase_2" in augmented_videos[i]:
            # print("phase 2 chunk: ", phase_2_chunk)
            augmented_chunk_index = (phase_2_chunk - 1) * CHUNK_LEN + version - 1
            if phase_2_incidents[video_no] == 'Frame Drop':
                framerate[augmented_chunk_index] = 10  # framerate changed to 10 fps
            else:
                rebuffering_duration[augmented_chunk_index] = 1
                # realign rest of video frames
                del vmaf[augmented_chunk_index]
                del psnr[augmented_chunk_index]
                del ssim[augmented_chunk_index]
        else:
            _, name = augmented_videos[i].split("-")
            # buffers in middle of video
            augmented_chunk_index = (int(name.split(".")[0][-1]) - 1) * CHUNK_LEN + 2 - 1
            # video buffers at this index
            rebuffering_duration[augmented_chunk_index] = 1
            # realign rest of video frames
            del vmaf[augmented_chunk_index]
            del psnr[augmented_chunk_index]
            del ssim[augmented_chunk_index]

        head, end = augmented_videos[i].split("-")
        name, ext = end.split(".")
        # print(name)

        # currently split into 20 chunks; group into 4 second chunks for phase 1, except for the ones by phase 2
        chunk_len = 4
        chunks = []

        for i in range(0, 5):
            if phase_2_chunk == i + 1:
                for j in range(0, CHUNK_LEN):
                    index = i * CHUNK_LEN + j
                    chunks.append([representation_index[index],  # video no
                                   rebuffering_duration[index] + rebuffer_times[index],  # rebuffer
                                   bitrates[index],  # bitrate
                                   chunk_durations[index],  # chunk len = 1s
                                   framerate[index],  # framerate (either original or 10)
                                   width[index],  # width
                                   height[index],  # height
                                   mos[index],  # mos
                                   psnr[index],  # psnr
                                   ssim[index],  # ssim
                                   vmaf[index]]  # vmaf
                                  )
            else:
                index = i * CHUNK_LEN
                end_index = index + CHUNK_LEN
                selected_rebuffer = np.sum(rebuffering_duration[index:end_index]) + np.sum(
                    rebuffer_times[index:end_index])
                chunks.append([representation_index[index],  # video no
                               selected_rebuffer,  # if rebuffer, how long
                               np.mean(bitrates[index:end_index]),  # mean bitrate of chunk
                               CHUNK_LEN,  # chunk len = 4s
                               np.mean(framerate[index:end_index]),  # framerate
                               np.mean(width[index:end_index]),  # width
                               np.mean(height[index:end_index]),  # height
                               np.mean(mos[index:end_index]),  # mean mos
                               np.mean(psnr[index:end_index]),  # mean psnr
                               np.mean(ssim[index:end_index]),  # mean ssim
                               np.mean(vmaf[index:end_index]),  # mean vmaf
                               ])

        df = pd.DataFrame(chunks, columns=["representation_index",
                                           "rebuffering_duration",
                                           "video_bitrate",
                                           "chunk_duration",
                                           "framerate",
                                           "width",
                                           "height",
                                           "mos",
                                           "psnr",
                                           "ssim",
                                           "vmaf"])
        # df = pd.DataFrame({
        #     "representation_index": representation_index,
        #     "rebuffering_duration": rebuffering_duration,
        #     "video_bitrate": bitrates,
        #     "chunk_duration": chunk_durations,
        #     "framerate": framerate,
        #     "width": width,
        #     "height": height,
        #     "mos": mos,
        #     "psnr": psnr,
        #     "ssim": ssim,
        #     "vmaf": vmaf
        # })
        if abr == "weights":
            df = df.drop(columns=["video_bitrate"])
        df.to_csv(out_path + name + ".csv", index=False)
    return


def create_main_data_file(out_path, log_path, abr):
    if not os.path.exists(out_path):
        return

    file_names = []
    mos = []
    content = []
    encoding_profile = []
    device = []

    for file in os.listdir(log_path):
        if abr == "weights":
            video_no = int(file.split(".")[0][-1])
            name = file.split("_")[0]
        else:
            trace_no_with_video_no = file.split("_")[0]
            name = trace_no_with_video_no.split("-")[1]
            video_no = video_names.index(name)
        file_names.append(file)
        content.append(video_categories[video_no])
        encoding_profile.append("H264")
        device.append("720p")
        video_qoe_score = get_qoe_by_chunk_for_video.get_augmented_video_qoe(video_no, file)
        # print(type(video_qoe_score))
        if isinstance(video_qoe_score, np.ndarray):
            mos.append(video_qoe_score[0] * 20)  # multiple by 20 to scale to x/100
        else:
            mos.append(video_qoe_score * 20)  # multiple by 20 to scale to x/100

    df = pd.DataFrame({
        "streaming_log": file_names,
        "mos": mos,
        "content": content,
        "encoding_profile": encoding_profile,
        "device": device
    })

    df.to_csv(out_path + "data.csv", index=False)
    return


def create_traces_only_for_weights():
    out_path_log_weights = "./custom_data/weights/streaming_logs/"
    out_path_main_weights = "./custom_data/weights/"
    dummy_trace_path = "../pysqoe/models/sensei/constant_bitrate_trace.log"

    # dummy trace path has neither delay nor changing bitrate
    for i in range(0, 8):
        create_streaming_logs(dummy_trace_path, i, out_path_log_weights, "weights")
    create_main_data_file(out_path_main_weights, out_path_log_weights, "weights")


def create_bba_traces():
    bba_trace_paths = "../../pensieve/test/results/bba/"
    bba_path_log = "./custom_data/bba/streaming_logs/"
    bba_path_main = "./custom_data/bba/"
    bba_extension = "bba"
    if not os.path.exists(bba_path_log):
        os.mkdir(bba_path_log)
    if not os.path.exists(bba_path_main):
        os.mkdir(bba_path_main)

    trace_index = 0
    for bba_trace in os.listdir(bba_trace_paths):
        print(bba_trace)
        for video_no in range(0, 8):
            out_path = bba_path_log + bba_extension + str(trace_index) + "-"
            create_streaming_logs(bba_trace_paths + bba_trace, video_no, out_path, "bba")
        trace_index += 1
    create_main_data_file(bba_path_main, bba_path_log, "bba")


def create_pensieve_traces():
    pensieve_trace_paths = "../../pensieve/test/results/pensieve/"
    pensieve_path_log = "./custom_data/pensieve/streaming_logs/"
    pensieve_path_main = "./custom_data/pensieve/"
    pensieve_extension = "pensieve"
    if not os.path.exists(pensieve_path_log):
        os.mkdir(pensieve_path_log)
    if not os.path.exists(pensieve_path_main):
        os.mkdir(pensieve_path_main)

    trace_index = 0
    for pensieve_trace in os.listdir(pensieve_trace_paths):
        print(pensieve_trace)
        for video_no in range(0, 8):
            out_path = pensieve_path_log + pensieve_extension + str(trace_index) + "-"
            create_streaming_logs(pensieve_trace_paths + pensieve_trace, video_no, out_path, "pensieve")
        trace_index += 1
    create_main_data_file(pensieve_path_main, pensieve_path_log, "pensieve")


def create_sensei_traces():
    sensei_trace_paths = "../../pensieve/test/results/sensei/"
    sensei_path_log = "./custom_data/sensei/"
    sensei_path_main = "./custom_data/sensei/"
    sensei_extension = "sensei"
    if not os.path.exists(sensei_path_log):
        os.mkdir(sensei_path_log)
    if not os.path.exists(sensei_path_main):
        os.mkdir(sensei_path_main)

    first_trace = ""
    first_run = True

    videos = 8
    all_traces = os.listdir(sensei_trace_paths)
    for video in range(0, videos):
        trace_index = 0
        video_name = "video" + str(video) + "/"
        if not os.path.exists(sensei_path_log + video_name):
            os.mkdir(sensei_path_log + video_name)
        if not os.path.exists(sensei_path_log + video_name + "streaming_logs/"):
            os.mkdir(sensei_path_log + video_name + "streaming_logs/")
        video_traces = [trace for trace in all_traces if video_name[0:-1] in trace]
        for trace in video_traces:
            out_path = sensei_path_log + video_name + "streaming_logs/" + "trace" + str(trace_index) + "-"
            create_streaming_logs(sensei_trace_paths + trace, video, out_path, "sensei")
            trace_index += 1
        create_main_data_file(sensei_path_main + video_name, sensei_path_log + video_name + "streaming_logs/", "sensei")
    return


# read from sensei folder and put in one big folder
def create_combined_sensei_traces():
    sensei_all_path_log = "./custom_data/sensei-all/streaming_logs/"
    sensei_all_path_main = "./custom_data/sensei-all/"

    sensei_path_logs = "./custom_data/sensei/"

    if not os.path.exists(sensei_all_path_main):
        os.mkdir(sensei_all_path_main)
    if not os.path.exists(sensei_all_path_log):
        os.mkdir(sensei_all_path_log)

    videos = 8
    for video in range(0, videos):
        path_to_video_logs = sensei_path_logs + "video" + str(video) +"/streaming_logs/"
        for file in os.listdir(path_to_video_logs):
            shutil.copy(path_to_video_logs + file, sensei_all_path_log)

    create_main_data_file(sensei_all_path_main, sensei_all_path_log, "sensei-all")
    return

def main():
    parse = argparse.ArgumentParser()
    parse.add_argument("-w", "--setweights", type=str,
                       help="Set weights or not. Use \"True\" to set weights and \"False\" to use real traces")
    args = parse.parse_args()

    if args.setweights.lower() == "true":
        create_traces_only_for_weights()
    else:
        create_bba_traces()
        create_pensieve_traces()
        create_sensei_traces()
        create_combined_sensei_traces()


if __name__ == "__main__":
    main()
