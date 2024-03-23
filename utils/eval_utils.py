import json, random, time, requests

url = "https://api.openai.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer $OPENAI_API_KEY"
}

def print_result(eval_results):
    with open("meta_info.json", 'r') as f:
        meta_infos = json.load(f)
    match_rate = 0  # the success rate of rule-based answer matching
    result_asp = {'action': 0, 'direction': 0, 'speed': 0, 'order': 0, 'attribute_change': 0}   # eval result under every temporal aspect
    qcount_asp = {'action': 0, 'direction': 0, 'speed': 0, 'order': 0, 'attribute_change': 0}   # question count result under every temporal aspect
    result_fasp = {'fine-grained action': 0, 'coarse-grained action': 0, 'object motion': 0, 'camera motion': 0, 
                   'absolute speed': 0, 'relative speed': 0, 'order': 0, 'color & light change': 0, 'size & shape change': 0, 'combined change': 0, 'other change': 0}  # eval result under every fine-grained temporal aspect
    qcount_fasp = {'fine-grained action': 0, 'coarse-grained action': 0, 'object motion': 0, 'camera motion': 0, 
                   'absolute speed': 0, 'relative speed': 0, 'order': 0, 'color & light change': 0, 'size & shape change': 0, 'combined change': 0, 'other change': 0}  # question count result under every fine-grained temporal aspect
    
    for id in eval_results:
        for asp in eval_results[id]:
            fasp = meta_infos[id.replace('.jpg', '').replace('.mp4', '')]["eval_dim"][asp]["type"] if asp!="order" else "order"
            for result in eval_results[id][asp]:
                result_asp[asp] += result["rating"]
                result_fasp[fasp] += result["rating"]
                qcount_asp[asp] += 1
                qcount_fasp[fasp] += 1
                if "match_success" in result:
                    match_rate += result["match_success"]

    match_rate = round(match_rate/sum(qcount_asp.values())*100, 1)
    result_asp['avg'] = round(sum(result_asp.values())*100/sum(qcount_asp.values()), 1)
    for asp in result_asp:
        if asp!='avg':
            result_asp[asp] = round(result_asp[asp]*100/qcount_asp[asp], 1)
    for fasp in result_fasp:
        result_fasp[fasp] = round(result_fasp[fasp]*100/qcount_fasp[fasp], 1)
    print("Accuracy Results:")
    print(result_asp)
    print(result_fasp)
    print(f"Match Success Rate={match_rate}")

def llm_output_to_rating(llm_output):
    assert 'Correct' in llm_output or 'Incorrect' in llm_output
    if llm_output.startswith('Correct'):
        rating = 1
    elif llm_output.startswith('Incorrect'):
        rating = 0
    elif ('Correct' in llm_output) and ('Incorrect' not in llm_output):
        rating = 1
    elif 'Incorrect' in llm_output:
        rating = 0
    return rating

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
    llm_output = dict_result['choices'][0]['message']['content'].strip()
    return llm_output

def get_eval_result(prompt, maxtry=10):
    llm_output = None
    while True:
        try:
            llm_output = get_llm_output(prompt)
            rating = llm_output_to_rating(llm_output)
            return llm_output, rating
        except:
            if maxtry<=0:
                return llm_output, 0
            maxtry -= 1
            print(f"Not success! {maxtry} retries remaining...")
            time.sleep(random.uniform(1, 2))