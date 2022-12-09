import numpy as np
import pandas as pd

VIDEO_LENGTH = 20  # video is 20 seconds
CHUNK_SIZE = 4  # chunks are 4s long

phase_1_crowdsourcing_qoe_path = "../../Phase 1 Chunk QoE - Sheet1.csv"
phase_2_crowdsourcing_qoe_path = "../../Phase 2 Chunk QoE - Sheet1.csv"

df_phase_1 = pd.read_csv(phase_1_crowdsourcing_qoe_path)
df_phase_2 = pd.read_csv(phase_2_crowdsourcing_qoe_path)

df_index_phase_1 = df_phase_1[['Survey A',
                               'Survey B',
                               'Survey C',
                               'Survey D',
                               'Survey E',
                               'Survey F',
                               'Phase 2 Chunk']]
df_qoe_phase_1 = df_phase_1[['Survey A QoE',
                             'Survey B QoE',
                             'Survey C QoE',
                             'Survey D QoE',
                             'Survey E QoE',
                             'Survey F QoE', ]]

df_index_phase_2 = df_phase_2[['Survey A',
                               'Survey B',
                               'Survey C',
                               'Survey D',
                               'Survey E', ]]
df_qoe_phase_2 = df_phase_2[['Survey A QoE',
                             'Survey B QoE',
                             'Survey C QoE',
                             'Survey D QoE',
                             'Survey E QoE', ]]


# video number should be 0 - 7
def get_qoe_by_chunks(video_no):
    chunks = np.ones(20) * -1
    video_index_phase_1 = df_index_phase_1.iloc[video_no]
    video_qoe_phase_1 = df_qoe_phase_1.iloc[video_no]
    video_index_phase_2 = df_index_phase_2.iloc[video_no]
    video_qoe_phase_2 = df_qoe_phase_2.iloc[video_no]

    for i in range(0, int(VIDEO_LENGTH / CHUNK_SIZE)):
        if i == video_index_phase_1['Phase 2 Chunk'] - 1:
            for j in range(0, CHUNK_SIZE):
                qoe_index = np.where(np.asarray(video_index_phase_2) == j + 1)[0]
                chunks[i * CHUNK_SIZE + j] = np.asarray(video_qoe_phase_2)[qoe_index]
        else:
            qoe_index = np.where(np.asarray(video_index_phase_1) == i + 1)[0]
            qoe = np.asarray(video_qoe_phase_1)[qoe_index]
            # print(qoe)
            for j in range(0, CHUNK_SIZE):
                chunks[i * CHUNK_SIZE + j] = qoe
                # print()
    qoe_ref_index = np.where(np.asarray(video_index_phase_1) == 0)[0]
    # chunk sensitivity, bigger dip means more reward
    chunks = np.abs((chunks - np.asarray(video_qoe_phase_1)[qoe_ref_index][0]))
    return chunks


print(get_qoe_by_chunks(2))
