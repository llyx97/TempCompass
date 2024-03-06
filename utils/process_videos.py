from moviepy.video.io.VideoFileClip import VideoFileClip
import json, os, argparse, shutil
from tqdm import tqdm


video_root = '../videos'
info_root = 'process_infos'

def clip_videos(mode):
    with open(f"{info_root}/clip_info.json", 'r') as f:
        infos = json.load(f)

    for vf in tqdm(infos):
        start_time, end_time = infos[vf]['start'], infos[vf]['end']
        video_clip = VideoFileClip(f"{video_root}/{vf}")
        if video_clip.duration<=(end_time-start_time+0.5):  # If the video has already been clipped, continue
            continue
        command = f"python process_single_video.py --input_file {video_root}/{vf} --mode {mode} --start_time {start_time} --end_time {end_time}"
        os.system(command)

def accelerate_videos(mode):
    video_clip = VideoFileClip(f"{video_root}/15695290.mp4")    # We accelerate this 84s video 4x, to 21s
    if video_clip.duration>30:
        command = f"python process_single_video.py --input_file {video_root}/15695290.mp4 --mode {mode} --acceleration_factor 4"
        os.system(command)

def reverse_videos(mode):
    with open(f"{info_root}/reverse_info.txt", 'r') as f:
        vids = f.read().strip().split(',')

    for vid in tqdm(vids):
        if os.path.isfile(f"{video_root}/{vid}_reverse.mp4"):
            continue
        command = f"python process_single_video.py --input_file {video_root}/{vid}.mp4 --mode {mode}"
        os.system(command)

def concat_accel_spatial_videos(mode):
    with open(f"{info_root}/speed_concat_info.json", 'r') as f:
        infos = json.load(f)
    for vid in tqdm(infos):
        vfiles = [f"{video_root}/{vid}_concat_{i}.mp4" for i in range(3)]
        if all(os.path.isfile(file) for file in vfiles):    # if the conflicting videos have been constructed, continue
            continue
        acceleration_factor = infos[vid]
        command = f"python process_single_video.py --input_file {video_root}/{vid}.mp4 --mode {mode} --acceleration_factor {acceleration_factor}"
        os.system(command)
    
    # Delete the three videos, which are used to construct conflicting videos, but themselves are not involved in the benchmark
    for vid in ['1100058499', '1092813279', '1084518106']:
        vfiles = [f"{video_root}/{vid}_concat_{i}.mp4" for i in range(3)]
        if all(os.path.isfile(file) for file in vfiles):
            os.remove(f"{video_root}/{vid}.mp4")

def concat_spatial(mode):
    vid_pairs = []
    with open(f"{info_root}/event_order_concat_info.txt", 'r') as f:
        lines = f.readlines()
    for l in lines:
        vid_pairs.append(l.strip().split(','))

    for vid_pair in vid_pairs:
        if os.path.isfile(f"{video_root}/{vid_pair[0]}_{vid_pair[1]}_0.mp4"):
            continue
        command = f"python process_single_video.py --input_file {video_root}/{vid_pair[0]}.mp4 --input_file2 {video_root}/{vid_pair[1]}.mp4 --mode {mode}"
        os.system(command)

def concat_temporal(mode):
    vid_pairs = []
    with open(f"{info_root}/event_order_concat_info.txt", 'r') as f:
        lines = f.readlines()
    for l in lines:
        vid_pairs.append(l.strip().split(','))

    for vid_pair in vid_pairs:
        vfiles = [f"{video_root}/{vid_pair[0]}_{vid_pair[1]}_{i}.mp4" for i in range(1,3)]
        if all(os.path.isfile(file) for file in vfiles):     # if the conflicting videos have been constructed, continue
            continue
        command = f"python process_single_video.py --input_file {video_root}/{vid_pair[0]}.mp4 --input_file2 {video_root}/{vid_pair[1]}.mp4 --mode {mode}"
        os.system(command)

if __name__ == "__main__":    
    parser = argparse.ArgumentParser()        
    parser.add_argument('--mode', default='all_in_once', choices=['clip', 'accelerate', 'reverse', 'concat_accel_spatial', 'concat_spatial', 'concat_temporal', 'all_in_once'])
    args = parser.parse_args()

    if args.mode=='all_in_once':
        clip_videos(mode='clip')
        accelerate_videos(mode='accelerate')
        reverse_videos(mode='reverse')
        concat_spatial(mode='concat_spatial')
        concat_temporal(mode='concat_temporal')
        concat_accel_spatial_videos(mode='concat_accel_spatial')
    elif args.mode=='clip':
        clip_videos(args.mode)
    elif args.mode=='reverse':
        reverse_videos(args.mode)
    elif args.mode=='accelerate':
        accelerate_videos(args.mode)
    elif args.mode=='concat_accel_spatial':
        concat_accel_spatial_videos(args.mode)
    elif args.mode=='concat_spatial':
        concat_spatial(args.mode)
    elif args.mode=='concat_temporal':
        concat_temporal(args.mode)