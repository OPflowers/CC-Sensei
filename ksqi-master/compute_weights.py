import pandas as pd
import numpy as np
import os
import copy
import data.get_qoe_by_chunk_for_video

q_i_filepath = "pysqoe/models/sensei/q_i_logs.txt"
weights_file = "pysqoe/models/sensei/weights.txt"

video_names = ["08e1", "4b69", "2c06", "6658", "6403", "06a6", "2abf", "1a6d"]

VIDEOS_REPRESENTATION = 8
NUM_CHUNKS = 8  # total number of chunks, regardless of chunk duration

# clear weights file
if os.path.exists(weights_file):
    with open(weights_file, 'w') as f:
        f.close()

# make column titles {video_name, q_0, q_1, ..., q_i}
q_i_title = []
for i in range(0, NUM_CHUNKS):
    q_i_title.append("q_" + str(i))

q_i_title_full = copy.deepcopy(q_i_title)
q_i_title_full.insert(0, "representation_index")  # add video number
q_i_title_full.insert(0, "video_name")  # add video file
q_i_title_full.append("qoe")  # add video crowdsourced qoe

df_qi = pd.DataFrame(columns=q_i_title_full)

with open(q_i_filepath) as f:
    for line in f:
        line_parse = line[1:-2]  # remove brackets and newline operator
        line_parse = line_parse.split(", ")  # split by comma + space
        video_file = line_parse[0]
        video_name = video_file.split(".")[0].split("/")[-1]  # extract video identifier

        line_parse[0] = video_name

        offset = 2  # 0 is for video file, 1 is for video index
        for i in range(offset, len(line_parse)):
            line_parse[i] = float(line_parse[i])
            # print(type(line_parse[i]))

        augmented_video_qoe = data.get_qoe_by_chunk_for_video.get_augmented_video_qoe(int(float(line_parse[1])),
                                                                                      video_file)
        if isinstance(augmented_video_qoe, np.ndarray):
            augmented_video_qoe = augmented_video_qoe[0]

        line_parse.append(augmented_video_qoe)
        # print("video name and qoe: ", video_file, augmented_video_qoe)
        df_qi = pd.concat([df_qi, pd.DataFrame(np.asarray(line_parse).reshape(1, -1), columns=q_i_title_full)], ignore_index=True)

with open(weights_file, 'a') as f:
    for name in video_names:
        video_qi = df_qi[df_qi['video_name'].str.contains(name)]

        df_linreg = pd.DataFrame(columns=q_i_title_full)
        chunk_num_max = 5
        for i in range(1, chunk_num_max + 1):
            video_name_for_chunk = name + "_" + str(i)
            video_qi_row = video_qi[video_qi['video_name'].str.contains(video_name_for_chunk)]

            if video_qi_row.empty:  # if name does not exist -> we did in phase 2 for closer evaluation
                phase_2_max = 4
                for j in range(1, phase_2_max + 1):
                    phase_2_video_name = name + "_phase_2_" + str(j)
                    video_qi_row_phase_2 = video_qi[video_qi['video_name'].str.contains(phase_2_video_name)]
                    df_linreg = pd.concat([df_linreg, video_qi_row_phase_2], ignore_index=True)
            else:
                df_linreg = pd.concat([df_linreg, video_qi_row], ignore_index=True)

        Q = df_linreg['qoe'].astype(float).to_numpy() * 20  # convert to out of 100
        q_i = df_linreg[q_i_title].astype(float).to_numpy()
        # for i in range(0, len(q_i)):
        #     for j in range(0, len(q_i[0])):
        #         if isinstance(q_i[i][j], float):
        #             pass
        #         else:
        #             print("element at i, j: ", i, j, q_i[i][j])
        #             print(type(q_i[i][j]))

        print(name)
        print(np.linalg.det(q_i))
        weights = np.linalg.solve(q_i, Q)


        f.write(name + " ")
        for weight in weights:
            f.write(str(weight) + " ")
        f.write("\n")

