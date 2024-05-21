from prompt_templates import *
from utils.eval_utils import *

import json, os
from tqdm import tqdm

qtype = "caption_matching"
input_file = "questions/multi-choice.json"
output_file = f"questions/{qtype}.json"
base_prompt = caption_matching_question_generation_prompt

os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Loading meta-information or multi-choice questions
with open(input_file, 'r') as f:
    mc_questions = json.load(f)

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

for id in tqdm(mc_questions):
    if id not in questions or questions[id] is None:
        questions[id] = {}
    for dim in mc_questions[id]:
        if mc_questions[id][dim] is not None and (dim not in questions[id] or not questions[id][dim]):
            mc_questions_str = '\n'.join([str(q) for q in mc_questions[id][dim][:2]])
            prompt = f"""{base_prompt}\nMulti-Choice Questions:\n{mc_questions_str}\nGenerate the true and false captions, do NOT show the multi-choice question in your response:"""

            extracted_questions = get_gen_question(prompt, sys_prompt="You are an AI assistant for question generation.", qtype=qtype)
            questions[id][dim] = extracted_questions

    with open(os.path.expanduser(output_file), "w") as f:
        json.dump(questions, f, indent=4)