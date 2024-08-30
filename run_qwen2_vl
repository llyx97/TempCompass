from transformers import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
import torch, os, json, argparse
from tqdm import tqdm


def inference_single_video(video_path, inp, model, processor):
    # Messages containing a video and a text query
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "video",
                    "video": video_path,
                    "max_pixels": 720 * 720,
                    "fps": 1.0,
                },
                {"type": "text", "text": inp},
            ],
        }
    ]

    # Preparation for inference
    text = processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    )
    inputs = inputs.to("cuda")

    # Inference
    generated_ids = model.generate(**inputs, max_new_tokens=128)
    generated_ids_trimmed = [
        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    # print(output_text)
    return output_text[0]

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
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        "Qwen/Qwen2-VL-7B-Instruct",
        torch_dtype=torch.bfloat16,
        attn_implementation="flash_attention_2",
        device_map="auto",
    )
    processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-7B-Instruct")

    for vid, data in tqdm(input_datas.items()):
        if vid not in predictions:
            predictions[vid] = {}
            video_path = os.path.join(args.data_path, 'videos', f'{vid}.mp4')
            for dim, questions in data.items():
                predictions[vid][dim] = []
                for question in questions:
                    inp = question['question'] + answer_prompt[args.task_type]
                    video_llm_pred = inference_single_video(video_path, inp, model, processor)
                    predictions[vid][dim].append({'question': question['question'], 'answer': question['answer'], 'prediction': video_llm_pred})
            with open(pred_file, 'w') as f:
                json.dump(predictions, f, indent=4)
