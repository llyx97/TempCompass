from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.fx.speedx import speedx
from moviepy.editor import *
import os, argparse
import imageio
import shutil

def clip_video(input_file, output_file, start_time, end_time):
    video_clip = VideoFileClip(input_file)
    clipped_video = video_clip.subclip(start_time, end_time)
    clipped_video.write_videofile(output_file, codec="libx264", audio_codec="aac")
    video_clip.close()

def accelerate_video(input_file, output_file, acceleration_factor):
    clip = VideoFileClip(input_file)
    accelerated_clip = speedx(clip, factor=acceleration_factor)
    accelerated_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")

def concat_accel_spatial(input_file, acceleration_factor=1, cat_mode='up_down'):
    """
        Accelerate a video and concat the accelerated and original video
        cat_mode: choose from 'left_right' and 'up_down'
    """
    vid = os.path.basename(input_file).replace(".mp4", "")
    dirname = os.path.dirname(input_file)

    orig_clip = VideoFileClip(input_file)
    accelerated_clip = speedx(orig_clip, factor=acceleration_factor) if acceleration_factor!=1 else orig_clip.copy()
    
    duration = min(orig_clip.duration, accelerated_clip.duration)

    if cat_mode=="left_right":
        final_clip_1 = clips_array([[accelerated_clip, accelerated_clip]])
        final_clip_2 = clips_array([[orig_clip.subclip(0, duration), accelerated_clip.subclip(0, duration)]])
        final_clip_3 = clips_array([[accelerated_clip.subclip(0, duration), orig_clip.subclip(0, duration)]])
    elif cat_mode=="up_down":
        final_clip_1 = clips_array([[accelerated_clip], [accelerated_clip]])
        final_clip_2 = clips_array([[orig_clip.subclip(0, duration)], [accelerated_clip.subclip(0, duration)]])
        final_clip_3 = clips_array([[accelerated_clip.subclip(0, duration)], [orig_clip.subclip(0, duration)]])
    final_clips = [final_clip_1, final_clip_2, final_clip_3]
    
    for i, final_clip in enumerate(final_clips):
        if not os.path.isfile(args.input_file.replace(vid, vid+f"_concat_{i}")):
            final_clip.write_videofile(f"{dirname}/tmp{i}.mp4", codec="libx264", audio_codec="aac")
            os.rename(f"{dirname}/tmp{i}.mp4", args.input_file.replace(vid, vid+f"_concat_{i}"))

def concat_temporal(input_file1, input_file2):
    """
        Concat two videos in the temporal dimention
    """
    vid1, vid2 = os.path.basename(input_file1).replace(".mp4", ""), os.path.basename(input_file2).replace(".mp4", "")
    dirname = os.path.dirname(input_file1)

    video1 = VideoFileClip(input_file1)
    video2 = VideoFileClip(input_file2)

    if video1.size != video2.size:
        video2 = video2.resize(video1.size)

    final_video1 = concatenate_videoclips([video1, video2], method="compose")
    final_video2 = concatenate_videoclips([video2, video1], method="compose")

    final_video1.write_videofile(f"{dirname}/{vid1}_{vid2}_1.mp4", codec="libx264", audio_codec="aac")
    final_video2.write_videofile(f"{dirname}/{vid1}_{vid2}_2.mp4", codec="libx264", audio_codec="aac")

def concat_spatial(input_file1, input_file2, cat_mode="up_down"):
    """
        Concat two videos in the spatial dimention
    """
    vid1, vid2 = os.path.basename(input_file1).replace(".mp4", ""), os.path.basename(input_file2).replace(".mp4", "")
    dirname = os.path.dirname(input_file1)

    video1 = VideoFileClip(input_file1)
    video2 = VideoFileClip(input_file2)

    if video1.size != video2.size:
        video2 = video2.resize(video1.size)
    duration = min(video1.duration, video2.duration)
    
    if cat_mode=="left_right":
        final_clip = clips_array([[video1.subclip(0, duration), video2.subclip(0, duration)]])
    elif cat_mode=="up_down":
        final_clip = clips_array([[video1.subclip(0, duration)], [video2.subclip(0, duration)]])
    
    final_clip.write_videofile(f"{dirname}/{vid1}_{vid2}_0.mp4", codec="libx264", audio_codec="aac")

def reverse_video(input_file, output_file):
    reader = imageio.get_reader(input_file)
    fps = reader.get_meta_data()['fps']

    frames = [frame for frame in reader]

    writer = imageio.get_writer(output_file, fps=fps)

    for frame in reversed(frames):
        writer.append_data(frame)

    writer.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()     
    parser.add_argument('--input_file', default="videos/1067268406.mp4")     
    parser.add_argument('--input_file2', default="videos/1067427023.mp4")     
    parser.add_argument('--mode', default='concat_temporal', choices=['clip', 'accelerate', 'reverse', 'concat_accel_spatial', 'concat_spatial', 'concat_temporal'])
    parser.add_argument('--start_time', default=0, type=float)
    parser.add_argument('--end_time', default=10, type=float)
    parser.add_argument('--acceleration_factor', default=2, type=float)
    args = parser.parse_args()

    vid = os.path.basename(args.input_file).replace(".mp4", "")
    if args.mode=="clip":
        clip_video(args.input_file, 'tmp.mp4', args.start_time, args.end_time)
        shutil.move('tmp.mp4', args.input_file)
    elif args.mode=="accelerate":
        accelerate_video(args.input_file, 'tmp.mp4', args.acceleration_factor)
        shutil.move('tmp.mp4', args.input_file)
    elif args.mode=="concat_accel_spatial":
        concat_accel_spatial(args.input_file, args.acceleration_factor)
    elif args.mode=="concat_temporal":
        concat_temporal(args.input_file, args.input_file2)
    elif args.mode=="concat_spatial":
        concat_spatial(args.input_file, args.input_file2)
    elif args.mode=="reverse":
        reverse_video(args.input_file, args.input_file.replace(vid, vid+"_reverse"))