from prompt_templates import *

import json, os, argparse
from utils.eval_utils import *
from tqdm import tqdm

qtype = "multi-choice"
base_prompt = multi_choice_evaluation_prompt

def main(predictions, eval_results, output_file, disable_llm):
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

                if pred["prediction"] is None:  # In some cases the Video LLM may refuse to produce a response
                    eval_result = {"question": pred["question"], "gt-answer": pred["answer"], "video-llm-prediction": pred["prediction"], "match_success": False, "rating": 0}
                    eval_results[id][dim].append(eval_result)
                    continue

                pred["prediction"] = pred["prediction"].replace('</s>', '')
                eval_result = {"question": pred["question"], "gt-answer": pred["answer"], "video-llm-prediction": pred["prediction"], "match_success": True}

                # Some hand-crafted matching rules
                if pred["prediction"]==pred["answer"]:
                    eval_result["rating"] = 1
                elif pred["prediction"] in ["A", "B", "C", "D"]:
                    eval_result["rating"] = 1 if pred["prediction"]==pred["answer"][0] else 0
                elif any(pred["prediction"].startswith(prefix) for prefix in ['A.', 'B.', 'C.', 'D.']):
                    eval_result["rating"] = 1 if pred["prediction"].split('.')[0]==pred["answer"][0] else 0
                elif any(pred["prediction"].startswith(prefix) for prefix in ['A)', 'B)', 'C)', 'D)']):
                    eval_result["rating"] = 1 if pred["prediction"].split(')')[0]==pred["answer"][0] else 0
                elif disable_llm:
                    eval_result["match_success"] = False    
                    eval_result["rating"] = 0               # Fail to match answer in the video-llm response. Directly set rating to 0
                else:
                    eval_result["match_success"] = False    # Fail to match answer in the video-llm response. Use ChatGPT to evaluate.
                    prompt = f"""{base_prompt}\nMulti-Choice Question:\n{pred["question"]}\nGround-Truth Answer: {pred["answer"]}\nModel Prediction: {pred["prediction"]}"""
                    eval_result["chatgpt-response"], eval_result["rating"] = get_eval_result(prompt)

                eval_results[id][dim].append(eval_result)

    with open(os.path.expanduser(output_file), "w") as f:
        json.dump(eval_results, f, indent=4)
    
    print_result(eval_results)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--video_llm', default="video-llava")
    parser.add_argument('--disable_llm', action='store_true', help="Whether to disable llm evaluation")
    args = parser.parse_args()

    disable_suffix = "_disable_llm" if args.disable_llm else ""
    input_file = f"predictions/{args.video_llm}/{qtype}.json"
    output_file = f"auto_eval_results{disable_suffix}/{args.video_llm}/{qtype}.json"
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

    main(predictions, eval_results, output_file, args.disable_llm)