from prompt_templates import *
from utils.eval_utils import *

import json, os
from tqdm import tqdm

qtype = "multi-choice"
input_file = "meta_info.json"
output_file = f"questions/{qtype}.json"
base_prompt = multi_choice_question_generation_prompt

os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Loading meta-information or multi-choice questions
with open(input_file, 'r') as f:
    meta_infos = json.load(f)

# Loading already generated questions
if os.path.isfile(output_file):
    with open(output_file, 'r') as f:
        questions = json.load(f)
else:
    questions = {}

q_count = 0
for id in questions:
    for dim in questions[id]:
        if questions[id][dim] is not None:
            q_count += len(questions[id][dim])
print(f"{qtype} has {q_count} generated question")


for id, data in tqdm(meta_infos.items()):
    if id not in questions:
        questions[id] = {}
    for dim, meta_info in data['eval_dim'].items():
        if meta_info is not None and (dim not in questions[id] or questions[id][dim] is None):
            if "type" in meta_info:
                meta_info.pop("type")
            prompt = f"""{base_prompt}\nMeta-information: {str(meta_info)}\nGenerate 5 {qtype} questions and correct answers related to "{dim}". Generate the correct answer after every generated question. Separate the questions with the string "[SEP]" and don't list the number of questions."""

            extracted_questions = get_gen_question(prompt, sys_prompt="You are an AI assistant for question generation.", qtype=qtype)
            questions[id][dim] = extracted_questions

    with open(os.path.expanduser(output_file), "w") as f:
        json.dump(questions, f, indent=4)