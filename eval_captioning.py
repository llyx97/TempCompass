from prompt_templates import *

import requests, json, os, argparse, random, time
from utils.eval_utils import url, headers, print_result
from tqdm import tqdm

qtype = "captioning"
base_prompt = caption_evaluation_prompt

def parse_llm_output(llm_output, gt_answer):

    if llm_output=="invalid_request_error" or not llm_output:
        eval_result = {"rating": -1, "chatgpt-answer": None, "chatgpt-reasoning": None}
        return eval_result
    
    eval_result = {}
    lines = llm_output.split("\n")

    for line in lines:
        line = line.strip()
        if "Reasoning" in line:
            eval_result["chatgpt-reasoning"] = line.replace("Reasoning:", "").strip()
        if "Answer" in line:
            eval_result["chatgpt-answer"] = line.replace("Answer:", "").strip()

    if not "chatgpt-answer" in eval_result:
        eval_result["chatgpt-answer"] = llm_output
    if not "chatgpt-reasoning" in eval_result:
        eval_result["chatgpt-reasoning"] = None

    # Check if the chatgpt answer is the ground-truth answer
    answer_counts = sum(eval_result["chatgpt-answer"].count(prefix) for prefix in ['A.', 'B.', 'C.', 'D.'])     # calculate the number of 'A.', 'B.', 'C.', 'D.' in chatgpt-answer
    if eval_result["chatgpt-answer"].split(". ")[0]==gt_answer.split(". ")[0] and answer_counts==1:
        eval_result["rating"] = 1
    else:
        eval_result["rating"] = 0
    return eval_result

def get_llm_output(prompt):
    data = {
        "max_tokens": 128,
        "model": "gpt-3.5-turbo",
        "temperature": 1.0,
        "top_p": 1,
        "presence_penalty": 1,
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant for question answering."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data).encode('utf-8'))
    result = response.content.decode("utf-8")
    dict_result = json.loads(result)
    token_count = dict_result['usage']
    try:
        llm_output = dict_result['choices'][0]['message']['content'].strip()
    except:
        if "error" in dict_result and dict_result["error"]["type"]=="invalid_request_error":
            llm_output = "invalid_request_error"
        else:
            llm_output = ""
    return llm_output, token_count

def get_eval_result(prompt, mc_answer, maxtry=10):
    while True:
        try:
            llm_output, token_count = get_llm_output(prompt)
            eval_result = parse_llm_output(llm_output, gt_answer=mc_answer)
            eval_result["token_count"] = token_count
            return eval_result
        except:
            if maxtry<=0:
                eval_result = {"chatgpt-reasoning": None, "chatgpt-answer": None, "rating": -1, "token_count": None}
                return eval_result
            maxtry -= 1
            print(f"Not success! {maxtry} retries remaining...")
            time.sleep(random.uniform(1, 2))

def main(predictions, eval_results, output_file, mc_questions):
    for id in tqdm(predictions):

        if id not in eval_results:
            eval_results[id] = {}

        for dim, preds in predictions[id].items():

            if dim in eval_results[id] and eval_results[id][dim] and len(preds)==len(eval_results[id][dim]):    # skip if the eval result already exists
                continue
            eval_results[id][dim] = []

            for pred in preds:
                if "prediction" not in pred and "response" in pred:
                    pred["prediction"] = pred["response"]
                pred["prediction"] = pred["prediction"].replace('</s>', '')
                prompt = f"""{base_prompt}\nVideo Description:{pred["prediction"]}\nMulti-Choice Question:\n{mc_questions[id][dim][0]["question"]}\nAnswer:"""

                eval_result = get_eval_result(prompt, mc_answer=mc_questions[id][dim][0]["answer"])

                eval_result["video-llm-prediction"] = pred["prediction"]
                eval_result["gt-answer"] = mc_questions[id][dim][0]["answer"]
                eval_results[id][dim].append(eval_result)

    with open(os.path.expanduser(output_file), "w") as f:
        json.dump(eval_results, f, indent=4)

    print_result(eval_results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--video_llm', default="video-llava")
    args = parser.parse_args()

    input_file = f"predictions/{args.video_llm}/{qtype}.json"
    output_file = f"auto_eval_results/{args.video_llm}/{qtype}.json"
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    # Loading video-llm predictions and multi-choice questions
    with open(input_file, 'r') as f:
        predictions = json.load(f)

    # Loading already evaluated results
    if os.path.isfile(output_file):
        with open(output_file, 'r') as f:
            eval_results = json.load(f)
    else:
        eval_results = {}

    # Loading multi-choice questions
    with open("questions/multi-choice.json", 'r') as f:
        mc_questions = json.load(f)

    main(predictions, eval_results, output_file, mc_questions)