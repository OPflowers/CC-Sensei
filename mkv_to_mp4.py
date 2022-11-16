import ffmpeg
import os

# this code is copied from this source here to convert our files from mkv (which is Youtube UGC file format) to MP4:
# https://stackoverflow.com/questions/64519818/converting-mkv-files-to-mp4-with-ffmpeg-python


def convert_to_mp4(mkv_file):
    name, ext = os.path.splitext(mkv_file)
    out_name = name + ".mp4"
    ffmpeg.input(mkv_file).output(out_name).run()
    print("Finished converting {}".format(mkv_file))


video_folder = "C:/Users/justi/Documents/Graduate Classes/Cloud Computing/Project/Youtube Videos/Youtube UGC Videos Raw"

for path, folder, files in os.walk(video_folder):
    for file in files:
        if file.endswith('.mkv'):
            print("Found file: %s" % file)
            convert_to_mp4(os.path.join(video_folder, file))
        else:
            pass
