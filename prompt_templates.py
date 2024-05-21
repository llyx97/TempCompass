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


multi_choice_question_generation_prompt = """
You will receive a piece of meta-information in the form of JSON dictionary. The meta-information consists of a "subject" and a temporal dimension (related to "action", "speed", "order" or "attribute change"). \
Your task is to generate 5 multi-choice questions and a correct answer based on the meta-information. Ensure that the 5 questions are diverse in language, diverse in format and diverse in the set of choices. \
Ensure that the question can be answered from the given meta-information.

Here are some examples of meta-information and generated questions:
```
Meta-information: {"subject": "boy", "action": "playing basketball"}
Multi-Choice Question:
What is the boy doing in the video?
A. cooking
B. singing
C. playing basketball
Correct Answer: C. playing basketball

Meta-information: {"subject": "entire video", "speed": "normal speed"}
Multi-Choice Question:
What is the speed of the video?
A. normal speed
B. time-lapse
C. slow motion
Correct Answer: A. normal speed

Meta-information: {"subject": "car", "direction": "turning left"}
Multi-Choice Question:
In which direction is the car driving?
A. straightforward
B. leftwards
C. rightwards
Correct Answer: B. leftwards

Meta-information: {"subject": "girl", "event1": "dressing up", "event2": "leaving the room"}
Multi-Choice Question:
What is the girl doing?
A. dressing up and then leaving the room
B. entering the room and dressing up
C. turning off clothes and then leaving the room
D. entering the room and then turning off clothes
Correct Answer: A. dressing up and then leaving the room

Meta-information: {"subject": "balloon", "attribute_change": "exploding"}
Multi-choice Question:
What is happening to the balloon?
A. shrinking
B. stay in the same shape
C. exploding
Correct Answer: C. exploding
```
"""

caption_matching_question_generation_prompt = """
You will receive information about two multi-choice questions in the form of JSON dictionary. The dictionary consists of a "question" that describes the question and choices and an "answer" that describes the correct answer. \
Your task is to generate 1 true caption and 3 false captions. The true caption describes the correct "answer" of multi-choice question. The false captions describe other choices except for the correct "answer". \
Ensure that the generated captions are diverse in language and do NOT fabricate information that does not exist in the given multi-choice questions.

Here is an example of multi-choice questions and generated true and false captions:
```
Multi-Choice Questions:
{"question": "What is the person doing?\\nA. singing\\nB. cooking\\nC. sleeping", "answer": "B. cooking"}
{"question": "What is the action shown in the video?\\nA. drawing\\nB. cooking\\nC. reading", "answer": "B. cooking"}
True Caption:
A person is cooking.
False Captions:
A person is sleeping.
A video showing a person singing.
The person is reading.
```
"""

yes_no_question_generation_prompt = """
You will receive information about several multi-choice questions in the form of JSON dictionary. The dictionaries consist of a "question" that describes the question and choices and an "answer" that describes the correct answer. \
Your task is to generate a positive question and a negative question for each multi-choice question. The positive questions, which are related to the correct "answer" of multi-choice question, should be answered with "yes". \
The negative questions, which are related to other choices except for the correct "answer", should be answered with "no". \
Ensure that the generated questions are diverse in language and do NOT fabricate information that does not exist in the given multi-choice question.

Here is an example of multi-choice questions and generated positive and negative questions:
```
Multi-Choice Questions:
{"question": "What is the person doing?\\nA. singing\\nB. cooking\\nC. sleeping", "answer": "B. cooking"}
{"question": "What is the primary action of the person?\\nA. playing football\\nB. cooking\\nC. sleeping", "answer": "B. cooking"}
{"question": "Which of the following actions best describes the person?\\nA. singing\\nB. cooking\\nC. drinking tea", "answer": "B. cooking"}
Positive Questions:
{"question": "Is the person cooking?", "answer": "yes"}
{"question": "Is the primary action of the person about cooking?", "answer": "yes"}
{"question": "Is cooking best describes the person's action?", "answer": "yes"}
Negative Questions:
{"question": "Is the person sleeping?", "answer": "no"}
{"question": "Is the primary action of the person about playing football?", "answer": "no"}
{"question": "Is drinking tea best describes the person's action?", "answer": "no"}
```
"""