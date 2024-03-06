import json, os, requests
from tqdm import tqdm

video_root = '../videos'

def download_video(download_url, video_file):
    vid_path = os.path.join(video_root, video_file)
    if os.path.exists(vid_path):
        print("Video already exists:", vid_path)
        return video_file
    
    try:
        r = requests.get(download_url, stream=True)
        total_size = int(r.headers.get('content-length', 0))
        block_size = 1024
        t = tqdm(total=total_size, unit='iB', unit_scale=True)
        with open(vid_path, 'wb') as f:
            for data in r.iter_content(block_size):
                t.update(len(data))
                f.write(data)
        t.close()
        print("Video saved to", vid_path)
        return video_file
    except Exception as e:
        print(e)
        print("Download failed for", download_url)
        print("Please download video manually.")
        return None


def main():
    with open("../meta_info.json", 'r') as f:
        meta_infos = json.load(f)

    vids = []
    for vid in meta_infos:
        if not '_' in vid:
            vids.append(vid)
        elif '_reverse' in vid or '_concat' in vid:
            vids.append(vid.split('_')[0])
        else:
            vid_pair = vid.split('_')[:2]
            vids += vid_pair
    vids = list(set(vids))

    # Download raw videos
    for vid in vids:
        if (not '_' in vid) and (not os.path.isfile(f"{video_root}/{vid}.mp4")):  # For constructed videos, the vid contains '_'
            url = f"https://ak.picdn.net/shutterstock/videos/{vid}/preview/{vid}.mp4"
            print("Downloading video:", url)
            download_video(url, f"{vid}.mp4")


if __name__ == "__main__":
    if not os.path.exists(video_root):
        os.makedirs(video_root)
    
    main()