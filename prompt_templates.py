caption_evaluation_prompt = """
You will receive a video description and a multi-choice question. Your task is to choose the correct answer and briefly explain the reason why you choose the answer. \
If none of the choice candidates are correct or the video description lacks enough information to answer the question, just answer "None of the choices are correct". \
Please organize your response in this format:
```
Reasoning: [Your reason to obtain the answer]
Answer: [Your answer]
```

Here are some examples of video description, multi-choice question and the expected answer:
```
Video Description: A person is palying football.
Multi-Choice Question:
What is the person doing in the video?
A. cooking
B. palying football
C. playing basketball
D. reading book
Reasoning: The video description mentions that the person is playing football.
Answer: B. palying football

Video Description: A bird is flying clockwise.
Multi-Choice Question:
In which direction is the bird flying?
A. backwark
B. counter-clockwise
C. clockwise
D. downward
Reasoning: The video description mentions that the bird is flying clockwise
Answer: C. clockwise

Video Description: An air balloon is inflating.
Multi-Choice Question:
What is happening to the air balloon?
A. exploding
B. getting smaller
C. flying
Reasoning: The video description mentions that the air balloon is inflating, while none of the coices can be explained as inflating.
Answer: None of the choices are correct
```
"""

multi_choice_evaluation_prompt = """
You will receive a multi-choice question, the ground-truth answer and the prediction from a question answering (QA) model. \
Your task is to determine whether QA model prediction is correct, based on the question and ground-truth answer. \
If the prediction is correct, respond "Correct". If the prediction is incorrect, respond "Incorrect".
"""

yes_no_evaluation_prompt = """
You will receive a Yes/No question, the ground-truth answer and the prediction from a question answering (QA) model. \
Your task is to determine whether QA model prediction is correct, based on the question and ground-truth answer. \
If the prediction is correct, respond "Correct". If the prediction is incorrect, respond "Incorrect".
"""

caption_matching_evaluation_prompt = """
You will receive a caption matching question, the ground-truth answer and the prediction from a question answering (QA) model. \
Your task is to determine whether QA model prediction is correct, based on the question and ground-truth answer. \
If the prediction is correct, respond "Correct". If the prediction is incorrect, respond "Incorrect".
"""