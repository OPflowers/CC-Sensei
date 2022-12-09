import pandas as pd
import numpy as np

q_i_filepath = "pysqoe/models/sensei/q_i_logs.txt"

with open(q_i_filepath) as f:
    for line in f:
        video_q_i = list(line)
        print(video_q_i)
        break