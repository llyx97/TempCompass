from openai import OpenAI
from tqdm import tqdm
import base64, os, cv2, argparse, json, time

client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY'),
    base_url="your_url",
)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def encode_video(video_path, video_frame_path, max_num_frames):
    os.makedirs(video_frame_path, exist_ok=True)
    if len(os.listdir(video_frame_path))==0:
        split_video_into_frames(video_path, video_frame_path, max_num_frames)
    frame_files = [f"{video_frame_path}/{ff}" for ff in os.listdir(video_frame_path) if ff.endswith('.jpg')]
    frame_files = sorted(frame_files, key=lambda x: int(x.split('.')[0].split('_')[-1]))
    encoded_frms = []
    for ff in frame_files:
        encoded_frms.append(encode_image(ff))
    return encoded_frms

def split_video_into_frames(video_path, video_frame_path, n_parts=16):
    video = cv2.VideoCapture(video_path)
    
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # 计算每部分应该有多少帧（尽量均匀分配，但最后一部分可能不同）
    frames_per_part = total_frames // n_parts
    
    # 读取视频并分割
    for i in range(n_parts):
        # 跳转到该部分的第一帧
        video.set(cv2.CAP_PROP_POS_FRAMES, i * frames_per_part)
        
        # 读取该部分的第一帧
        ret, frame = video.read()
        if not ret:
            print("无法读取视频帧。")
            break
        
        # 保存帧为图片
        frame_number = i * frames_per_part  # 用于命名，确保唯一性
        cv2.imwrite(f"{video_frame_path}/frame_{frame_number}.jpg", frame)
    
    # 释放视频资源
    video.release()

def get_response(encoded_frms, prompt, model="gpt-4o-2024-05-13"):
    max_tokens = 128
    content = []
    if len(encoded_frms)>1:
        for fid, encoded_frm in enumerate(encoded_frms):
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_frm}"}})
    else:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_frms[0]}"}})
    content.append({"type": "text", "text": prompt})

    completion = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are an AI assistant for question answering."
            },
            {
                "role": "user",
                "content": content
            }
        ],
        max_tokens=max_tokens
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

def inference_single_video(video_path, video_frame_path, prompt, max_num_frames, maxtry=10):
    while True:
        try:
            encoded_frms = encode_video(video_path, video_frame_path, max_num_frames)
            llm_response = get_response(encoded_frms, prompt)
            time.sleep(1)
            return llm_response
        except:
            if maxtry<=0:
                return ""
            maxtry -= 1
            print(f"Not success! {maxtry} retries remaining...")
            time.sleep(10)

answer_prompt = {
    "multi-choice": "\nPlease directly give the best option:",
    "yes_no": "\nPlease answer yes or no:",
    "caption_matching": "\nPlease directly give the best option:",
    "captioning": ""    # The answer "Generated Caption:" is already contained in the question
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()     
    parser.add_argument('--data_path', default='path_to_tempcompass')     
    parser.add_argument('--output_path', default='predictions/gpt-4o')     
    parser.add_argument('--max_num_frames', default=8, type=int)
    parser.add_argument('--task_type', default='multi-choice', choices=['multi-choice', 'captioning', 'caption_matching', 'yes_no'])     
    args = parser.parse_args()

    # Loading questions
    question_path = f"{args.data_path}/questions/{args.task_type}.json"
    with open(question_path, 'r') as f:
        input_datas = json.load(f)

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)
    pred_file = f"{args.output_path}/{args.task_type}.json"
    # Loading existing predictions
    if os.path.isfile(pred_file):
        with open(f"{args.output_path}/{args.task_type}.json", 'r') as f:
            predictions = json.load(f)
    else:
        predictions = {}

    for vid, data in tqdm(input_datas.items()):
        if vid not in predictions:
            predictions[vid] = {}
            video_path = os.path.join(args.data_path, 'videos', f'{vid}.mp4')
            video_frame_path = os.path.join(args.data_path, 'video_frames', vid)
            for dim, questions in data.items():
                predictions[vid][dim] = []
                for question in questions:
                    inp = question['question'] + answer_prompt[args.task_type]
                    video_llm_pred = inference_single_video(video_path, video_frame_path, inp, args.max_num_frames)
                    predictions[vid][dim].append({'question': question['question'], 'answer': question['answer'], 'prediction': video_llm_pred})
            with open(pred_file, 'w') as f:
                json.dump(predictions, f, indent=4)
