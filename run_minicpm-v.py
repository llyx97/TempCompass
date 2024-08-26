import torch, argparse, json, os
from tqdm import tqdm
from PIL import Image
from transformers import AutoModel, AutoTokenizer
from decord import VideoReader, cpu    # pip install decord


MAX_NUM_FRAMES=64 # if cuda OOM set a smaller number

def encode_video(video_path):
    def uniform_sample(l, n):
        gap = len(l) / n
        idxs = [int(i * gap + gap / 2) for i in range(n)]
        return [l[i] for i in idxs]

    vr = VideoReader(video_path, ctx=cpu(0))
    sample_fps = round(vr.get_avg_fps() / 1)  # FPS
    frame_idx = [i for i in range(0, len(vr), sample_fps)]
    if len(frame_idx) > MAX_NUM_FRAMES:
        frame_idx = uniform_sample(frame_idx, MAX_NUM_FRAMES)
    frames = vr.get_batch(frame_idx).asnumpy()
    frames = [Image.fromarray(v.astype('uint8')) for v in frames]
    print(f'num frames: {len(frames)}')
    return frames

def inference_single_video(video_path, inp, model):
    frames = encode_video(video_path)
    msgs = [
        {'role': 'user', 'content': frames + [inp]}, 
    ]

    # Set decode params for video
    params={}
    params["use_image_id"] = False
    params["max_slice_nums"] = 2 # use 1 if cuda OOM and video resolution >  448*448

    answer = model.chat(
        image=None,
        msgs=msgs,
        tokenizer=tokenizer,
        **params
    )
    print(answer)
    return answer

answer_prompt = {
    "multi-choice": "\nPlease directly give the best option:",
    "yes_no": "\nPlease answer yes or no:",
    "caption_matching": "\nPlease directly give the best option:",
    "captioning": ""    # The answer "Generated Caption:" is already contained in the question
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()     
    parser.add_argument('--data_path', default='path_to_tempcompass')     
    parser.add_argument('--output_path', default='predictions')     
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

    # Loading Model
    model = AutoModel.from_pretrained('openbmb/MiniCPM-V-2_6', trust_remote_code=True,
        attn_implementation='sdpa', torch_dtype=torch.bfloat16) # sdpa or flash_attention_2, no eager
    model = model.eval().cuda()
    tokenizer = AutoTokenizer.from_pretrained('openbmb/MiniCPM-V-2_6', trust_remote_code=True)

    for vid, data in tqdm(input_datas.items()):
        if vid not in predictions:
            predictions[vid] = {}
            video_path = os.path.join(args.data_path, 'videos', f'{vid}.mp4')
            for dim, questions in data.items():
                predictions[vid][dim] = []
                for question in questions:
                    inp = question['question'] + answer_prompt[args.task_type]
                    video_llm_pred = inference_single_video(video_path, inp, model)
                    predictions[vid][dim].append({'question': question['question'], 'answer': question['answer'], 'prediction': video_llm_pred})
            with open(pred_file, 'w') as f:
                json.dump(predictions, f, indent=4)
