import videoeffects
import os

file_path_to_raw_videos_mp4 = \
    "C:/Users/justi/Documents/Graduate Classes/Cloud Computing/Project/Youtube Videos/Youtube UGC Videos Raw/"

file_path_for_output_videos = \
    "C:/Users/justi/Documents/Graduate Classes/Cloud Computing/Project/Augmented Videos/Phase 1/"

# code modified from this source:
# https://stackoverflow.com/questions/64519818/converting-mkv-files-to-mp4-with-ffmpeg-python
for path, folder, files in os.walk(file_path_to_raw_videos_mp4):
    for file in files:
        if file.endswith('.mp4'):
            print("Found file: %s" % file)
            videoeffects.create_many_buffers(file_path_to_raw_videos_mp4 + file, 5, 1,
                                             out_path=file_path_for_output_videos)
        else:
            pass

