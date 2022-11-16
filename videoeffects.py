import sys
from moviepy.editor import *
from moviepy.video.fx.all import resize, invert_colors, freeze, supersample


def splice_clip(clip, time, duration):
    start = clip.subclip(0, time)
    middle = clip.subclip(time, time + duration)
    end = clip.subclip(time + duration)
    return (start, middle, end)


# =====================================================

def insert_buffer(clip, time, duration):
    clip = freeze(clip, t=time, freeze_duration=duration)
    return clip


def create_many_buffers(filename, count, duration, **kwargs):
    out_path = kwargs.get("out_path", None)
    print("Filename: " + filename)
    video = VideoFileClip(filename)
    length = video.duration
    chunk_size = (float(length) / count)
    start_times = [(chunk_size * i + chunk_size/2) for i in range(count)]

    for i, s in enumerate(start_times):
        result = insert_buffer(video, s, duration)

        if out_path is not None:
            name, ext = filename.split(".")

            file_out = out_path + name.split("/")[-1] + "_" + str(i + 1) + ".mp4"
            print("Writing to: " + file_out)
            result.write_videofile(file_out)
        else:
            result.write_videofile(filename[:-4] + "_" + str(i + 1) + ".mp4")
            pass


# =====================================================

def insert_frame_drop(clip, time, duration, new_frame_rate):
    a, b, c = splice_clip(clip, time, duration)
    b.write_videofile("temp.mp4", new_frame_rate)
    b_modified = VideoFileClip("temp.mp4")
    final = concatenate_videoclips([a, b_modified, c])
    return final


def create_many_frame_drops(filename, count, duration, new_frame_rate):
    video = VideoFileClip(filename)
    length = video.duration
    start_times = [(float(length) / count) * i for i in range(count)]
    for i, s in enumerate(start_times):
        result = insert_frame_drop(video, s, duration, new_frame_rate)
        result.write_videofile(filename[:-4] + "_" + str(i + 1) + ".mp4")


# =====================================================

def insert_resolution_drop(clip, time, duration, old_resolution, new_resolution):
    a, b, c = splice_clip(clip, time, duration)
    b = b.resize(new_resolution)
    b = b.resize(old_resolution)
    final = concatenate_videoclips([a, b, c])
    return final


def create_many_resolution_drops(filename, count, duration, old_resolution, new_resolution):
    video = VideoFileClip(filename)
    length = video.duration
    start_times = [(float(length) / count) * i for i in range(count)]
    for i, s in enumerate(start_times):
        result = insert_frame_drop(video, s, duration, old_resolution, new_resolution)
        result.write_videofile(filename[:-4] + "_" + str(i + 1) + ".mp4")


# =====================================================

# usage example:
# create_many_buffers("Youtube Videos/Worlds Feature Faker vs Ryu.mp4", 5, 1)
