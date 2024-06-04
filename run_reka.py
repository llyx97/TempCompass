from reka.client import Reka
from reka import ChatMessage
import os, base64, argparse, json
from tqdm import tqdm

def video_to_url(video_path):
    with open(video_path, 'rb') as video_file:
        video_data = video_file.read()
        video_base64 = base64.b64encode(video_data).decode('utf-8')
        video_url = f'data:video/mp4;base64,{video_base64}'
    return video_url

def get_response(client, video_path, question):
    response = client.chat.create(
        messages=[
            ChatMessage(
                content=[
                    {"type": "video_url", "video_url": video_to_url(video_path)},
                    {"type": "text", "text": question}
                ],
                role="user",
            )
        ],
        model="reka-flash",
    )

    llm_response = response.responses[0].message.content
    return llm_response

answer_prompt = {
    "multi-choice": "\nPlease directly give the best option:",
    "yes_no": "\nPlease answer yes or no:",
    "caption_matching": "\nPlease directly give the best option:",
    "captioning": ""    # The answer "Generated Caption:" is already contained in the question
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()     
    parser.add_argument('--video_path', default='videos')     
    parser.add_argument('--output_path', default='predictions/reka-flash')     
    parser.add_argument('--task_type', default='multi-choice', choices=['multi-choice', 'captioning', 'caption_matching', 'yes_no'])     
    args = parser.parse_args()

    # Loading questions
    question_path = f"questions/{args.task_type}.json"
    with open(question_path, 'r') as f:
        input_datas = json.load(f)

    os.makedirs(args.output_path, exist_ok=True)
    pred_file = f"{args.output_path}/{args.task_type}.json"
    # Loading existing predictions
    if os.path.isfile(pred_file):
        with open(f"{args.output_path}/{args.task_type}.json", 'r') as f:
            predictions = json.load(f)
    else:
        predictions = {}

    # Setup REKA API and client
    reka_api_key = os.environ.get('REKA_API_KEY')
    client = Reka(api_key=reka_api_key)

    for vid, data in tqdm(input_datas.items()):
        if vid not in predictions:
            print(vid)
            predictions[vid] = {}
            video_path = os.path.join(args.video_path, f'{vid}.mp4')
            for dim, questions in data.items():
                predictions[vid][dim] = []
                for question in questions:
                    inp = question['question'] + answer_prompt[args.task_type]
                    video_llm_pred = get_response(client, video_path, inp)
                    predictions[vid][dim].append({'question': question['question'], 'answer': question['answer'], 'prediction': video_llm_pred})
            with open(pred_file, 'w') as f:
                json.dump(predictions, f, indent=4)