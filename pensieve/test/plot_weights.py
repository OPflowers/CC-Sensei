import os
import matplotlib.pyplot as plt
import get_qoe_by_chunk_for_video


print(os.getcwd())

for video_no in range(0, 8):
    weights = get_qoe_by_chunk_for_video.get_weights(video_no)

    plt.plot(weights)
    plt.show()