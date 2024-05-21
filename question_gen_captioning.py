import json, os
from tqdm import tqdm

qtype = "captioning"
input_file = "questions/multi-choice.json"
meta_info_file = "meta_info.json"
output_file = f"questions/{qtype}.json"
os.makedirs(os.path.dirname(output_file), exist_ok=True)

question_templates = [
    "You will be presented with a video and several pieces of information. One piece of information is consistent with the video while the others are not. Please identify the information that consistent with the video and generate a video caption accordingly.",
    "A video and multiple pieces of information will be provided to you. One of these pieces of information matches the content of the video, while the remaining ones do not. Your objective is to pinpoint the information that is in harmony with the video and craft a suitable video caption.",
    "You will be presented with a video and several pieces of information. One piece of information is consistent with the video while the others are not. Please identify the information that consistent with the video and generate a video caption accordingly. Ensure that the generated video caption is brief.",
    "A video and multiple pieces of information will be provided to you. One of these pieces of information matches the content of the video, while the remaining ones do not. Your objective is to pinpoint the information that is in harmony with the video and craft a suitable video caption. Ensure that the generated video caption is brief."
]

def parse_mc_question(mc_question, meta_info, dim):
    """
        Extract the options from the multi-choice question and convert them into the following text form
        Information A: {”subject”: “person”, “action”: “cooking”}
        Information B: {”subject”: “person”, “action”: “singing”}
    """
    option_list = mc_question.split("\n")[1:]
    option_list = [option.replace("A.", "").replace("B.", "").replace("C.", "").replace("D.", "").strip() for option in option_list]

    info_text = ""
    subject = meta_info["subject"]
    for option, character in zip(option_list, ["A", "B", "C", "D"][:len(option_list)]):
        info_ = {"subject": subject, dim: option}
        info_text += f"Information {character}: {info_}\n"
    return info_text


# Loading meta-information or multi-choice questions
with open(input_file, 'r') as f:
    input_datas = json.load(f)
with open(meta_info_file, 'r') as f:
    meta_info = json.load(f)

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

for id, data in tqdm(input_datas.items()):
    if id not in questions:
        questions[id] = {}
    for dim, mc_questions in data.items():
        if mc_questions is not None and (dim not in questions[id] or not questions[id][dim]):
            questions[id][dim] = []
            option_text = parse_mc_question(mc_questions[0]["question"], meta_info[id]["eval_dim"][dim], dim)
            for template in question_templates:
                question = f"{template}\n{option_text}Generated Caption:"
                questions[id][dim].append({"question": question, "answer": mc_questions[0]["answer"]})

    with open(os.path.expanduser(output_file), "w") as f:
        json.dump(questions, f, indent=4)